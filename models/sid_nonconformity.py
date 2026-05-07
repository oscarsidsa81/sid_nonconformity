# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SidNonconformity(models.Model):
    _name = 'sid.nonconformity'
    _description = 'No conformidad SID'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_detected desc, id desc'

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True,
    )
    title = fields.Char(string='Título', required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='company_id.currency_id',
        readonly=True,
        store=True,
    )

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('open', 'Abierta'),
        ('action', 'Acción Correctiva'),
        ('verify', 'Verificación de Eficacia'),
        ('done', 'Cerrada'),
        ('cancel', 'Cancelada'),
    ], string='Estado', default='draft', required=True, tracking=True)

    iso_scope = fields.Selection([
        ('iso_9001', 'ISO 9001'),
        ('iso_14001', 'ISO 14001'),
        ('integrated', 'ISO 9001 + ISO 14001 Integrado'),
    ], string='Alcance ISO', default='iso_9001', required=True, tracking=True)

    nc_type = fields.Selection([
        ('supplier', 'Proveedor / Compra'),
        ('customer', 'Reclamación de Cliente'),
        ('warehouse', 'Almacén / Logística'),
        ('product', 'Producto / Especificación'),
        ('process', 'Proceso Interno'),
        ('environment', 'Incidente Ambiental'),
        ('audit', 'Incidencia de Auditoría'),
        ('other', 'Otro'),
    ],
    string='Tipo',
    default='process',
    required=True,
    tracking=True,
    help=(
        'Define la casuística de la NC y qué reportes externos pueden aplicar.\n'
        '- Proveedor / Compra: orientada a proveedor (normalmente interno + proveedor).\n'
        '- Reclamación de Cliente: orientada a cliente (normalmente interno + cliente; puede incluir proveedor si hay compra/proveedor vinculado).\n'
        '- Almacén / Logística, Producto, Proceso, Ambiental, Auditoría, Otro: tipologías para clasificación interna y trazabilidad.'
    ),
)

    severity = fields.Selection([
        ('minor', 'Baja'),
        ('major', 'Alta'),
        ('critical', 'Crítica'),
    ], string='Importancia', default='minor', tracking=True)

    priority = fields.Selection([
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ], string='Prioridad', default='normal', tracking=True)

    user_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user,
        tracking=True,
    )
    reviewer_id = fields.Many2one('res.users', string='Revisor', tracking=True)

    date_detected = fields.Date(
        string='Fecha de detección',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    date_deadline = fields.Date(string='Fecha límite', tracking=True)
    date_closed = fields.Date(string='Fecha de cierre', readonly=True, tracking=True)
    is_overdue = fields.Boolean(string='Vencida', compute='_compute_dates', store=True)
    days_open = fields.Integer(string='Días abierta', compute='_compute_dates')
    days_to_close = fields.Integer(string='Días para cerrar', compute='_compute_dates', store=True)

    supplier_id = fields.Many2one('res.partner', string='Proveedor', tracking=True, domain="[('is_company', '=', True), ('supplier_rank', '>', 0)]")
    customer_id = fields.Many2one('res.partner', string='Cliente', tracking=True, domain="[('is_company', '=', True), ('customer_rank', '>', 0)]")
    product_id = fields.Many2one('product.product', string='Producto', tracking=True)
    lot_id = fields.Many2one('stock.production.lot', string='Lote / Número de serie', tracking=True)
    quantity_affected = fields.Float(string='Cantidad afectada', tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UdM')
    estimated_cost = fields.Monetary(string='Costo estimado', currency_field='currency_id', tracking=True)
    amount_customer = fields.Monetary(string='Importe final - Cliente', currency_field='currency_id', tracking=True)
    amount_sidsa = fields.Monetary(string='Importe final - SIDSA', currency_field='currency_id', tracking=True)
    amount_supplier = fields.Monetary(string='Importe final - Proveedor', currency_field='currency_id', tracking=True)


    assume_cost_customer = fields.Boolean(string='Costo asumido por cliente', tracking=True)
    assume_cost_sidsa = fields.Boolean(string='Costo asumido por SIDSA', tracking=True)
    assume_cost_supplier = fields.Boolean(string='Costo asumido por proveedor', tracking=True)

    available_sale_order_ids = fields.Many2many(
        'sale.order',
        compute='_compute_available_sale_order_ids',
        string='Pedidos de venta disponibles',
    )

    purchase_id = fields.Many2one('purchase.order', string='Pedido de compra', tracking=True)
    sale_id = fields.Many2one('sale.order', string='Pedido de venta', tracking=True)
    picking_id = fields.Many2one('stock.picking', string='Albarán', tracking=True)
    move_line_id = fields.Many2one('stock.move.line', string='Línea de operación', tracking=True)

    description = fields.Html(string='Descripción / Evidencia', tracking=True, sanitize=True)
    containment_action = fields.Html(string='Acciones Inmediatas', tracking=True)
    root_cause = fields.Html(string='Causa Raíz', tracking=True)
    corrective_action = fields.Html(string='Acciones Correctivas', tracking=True)
    preventive_action = fields.Html(string='Acción preventiva / Tratamiento del riesgo', tracking=True)
    effectiveness_check = fields.Html(string='Validación', tracking=True)
    closing_notes = fields.Text(string='Notas de cierre', tracking=True)
    environmental_impact = fields.Text(string='Impacto ambiental / Controles', tracking=True)

    attachment_count = fields.Integer(string='Adjuntos', compute='_compute_attachment_count')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sid.nonconformity') or _('New')
        record = super().create(vals)
        if record.user_id:
            record.message_subscribe(partner_ids=record.user_id.partner_id.ids)
        return record

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id and not rec.uom_id:
                rec.uom_id = rec.product_id.uom_id



    @api.constrains('assume_cost_customer', 'assume_cost_sidsa', 'assume_cost_supplier', 'amount_customer', 'amount_sidsa', 'amount_supplier')
    def _check_assumed_cost_amounts(self):
        for rec in self:
            if rec.assume_cost_customer and not rec.amount_customer:
                raise ValidationError(_('El importe de cliente es obligatorio cuando el cliente asume el costo.'))
            if rec.assume_cost_sidsa and not rec.amount_sidsa:
                raise ValidationError(_('El importe de SIDSA es obligatorio cuando SIDSA asume el costo.'))
            if rec.assume_cost_supplier and not rec.amount_supplier:
                raise ValidationError(_('El importe de proveedor es obligatorio cuando el proveedor asume el costo.'))


    @api.onchange('purchase_id')
    def _onchange_purchase_id(self):
        for rec in self:
            if rec.purchase_id:
                rec.supplier_id = rec.purchase_id.partner_id

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        for rec in self:
            if rec.sale_id:
                rec.customer_id = rec.sale_id.partner_id

    @api.depends('purchase_id', 'supplier_id')
    def _compute_available_sale_order_ids(self):
        for rec in self:
            sale_orders = self.env['sale.order']
            if rec.purchase_id:
                sale_orders = rec.purchase_id.order_line.mapped('sale_line_id.order_id')
            if rec.supplier_id:
                supplier_purchases = self.env['purchase.order'].search([
                    ('partner_id', '=', rec.supplier_id.id)
                ])
                supplier_sales = supplier_purchases.order_line.mapped('sale_line_id.order_id')
                sale_orders |= supplier_sales
            rec.available_sale_order_ids = sale_orders

    @api.depends('date_detected', 'date_deadline', 'date_closed', 'state')
    def _compute_dates(self):
        today = fields.Date.context_today(self)
        for rec in self:
            start = rec.date_detected or today
            end = rec.date_closed or today
            rec.days_open = (end - start).days if start and end and rec.state not in ('done', 'cancel') else 0
            rec.days_to_close = (rec.date_closed - start).days if rec.date_closed and start else 0
            rec.is_overdue = bool(rec.date_deadline and rec.date_deadline < today and rec.state not in ('done', 'cancel'))

    def _compute_attachment_count(self):
        attachment_model = self.env['ir.attachment'].sudo()
        for rec in self:
            rec.attachment_count = attachment_model.search_count([
                ('res_model', '=', rec._name),
                ('res_id', '=', rec.id),
            ])


    def _post_phase_report_to_chatter(self, message=None):
        report_action = self.env.ref('sid_nonconformity.action_report_sid_nonconformity', raise_if_not_found=False)
        if not report_action:
            return
        for rec in self:
            pdf_content, _report_type = report_action._render_qweb_pdf(rec.id)
            attachment = self.env['ir.attachment'].create({
                'name': 'NC-%s-%s.pdf' % (rec.name, rec.state),
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'mimetype': 'application/pdf',
                'res_model': rec._name,
                'res_id': rec.id,
            })
            rec.message_post(
                body=message or _('Reporte de fase generado automáticamente.'),
                attachment_ids=[attachment.id],
            )

    def action_previous_phase(self):
        previous_state_map = {
            'open': 'draft',
            'action': 'open',
            'verify': 'action',
            'done': 'verify',
        }
        for rec in self:
            previous_state = previous_state_map.get(rec.state)
            if not previous_state:
                raise UserError(_('No hay una fase anterior disponible desde el estado actual.'))
            vals = {'state': previous_state}
            if previous_state != 'done':
                vals['date_closed'] = False
            rec.write(vals)

    def action_open(self):
        for rec in self:
            old_state = rec.state
            rec.write({'state': 'open'})
            if old_state == 'draft':
                rec._post_phase_report_to_chatter(
                    message=_('Reporte de fase generado automáticamente al pasar de Borrador a Abierta.')
                )

    def action_start_action(self):
        self.write({'state': 'action'})

    def action_verify(self):
        self.write({'state': 'verify'})

    def action_close(self):
        for rec in self:
            missing = []
            if not rec.root_cause:
                missing.append(_('Análisis de causa raíz'))
            if not rec.corrective_action:
                missing.append(_('Acción correctiva'))
            if rec.state == 'verify' and not rec.effectiveness_check:
                missing.append(_('Verificación de eficacia'))
            if not any([rec.assume_cost_customer, rec.assume_cost_sidsa, rec.assume_cost_supplier]):
                missing.append(_('Al menos una responsabilidad de costo (Cliente, SIDSA, Proveedor)'))
            if missing:
                raise UserError(_('No puede cerrar la no conformidad hasta completar estos campos: %s') % ', '.join(missing))
            rec.write({'state': 'done', 'date_closed': fields.Date.context_today(rec)})
            rec._post_phase_report_to_chatter(
                message=_('Formulario PDF generado automáticamente al cerrar la no conformidad.')
            )

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft', 'date_closed': False})

    def action_view_attachments(self):
        self.ensure_one()
        return {
            'name': _('Adjuntos'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'context': {'default_res_model': self._name, 'default_res_id': self.id},
        }
