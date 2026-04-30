# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SidNonconformity(models.Model):
    _name = 'sid.nonconformity'
    _description = 'SID Nonconformity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_detected desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True,
    )
    title = fields.Char(string='Title', required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
        store=True,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('action', 'Corrective Action'),
        ('verify', 'Effectiveness Check'),
        ('done', 'Closed'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    iso_scope = fields.Selection([
        ('iso_9001', 'ISO 9001'),
        ('iso_14001', 'ISO 14001'),
        ('integrated', 'ISO 9001 + ISO 14001'),
    ], string='ISO Scope', default='iso_9001', required=True, tracking=True)

    nc_type = fields.Selection([
        ('supplier', 'Supplier / Purchase'),
        ('customer', 'Customer Claim'),
        ('warehouse', 'Warehouse / Logistics'),
        ('product', 'Product / Specification'),
        ('process', 'Internal Process'),
        ('environment', 'Environmental Incident'),
        ('audit', 'Audit Finding'),
        ('other', 'Other'),
    ], string='Type', default='process', required=True, tracking=True)

    severity = fields.Selection([
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ], string='Severity', default='minor', tracking=True)

    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='normal', tracking=True)

    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
    )
    reviewer_id = fields.Many2one('res.users', string='Reviewer', tracking=True)

    date_detected = fields.Date(
        string='Detection Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    date_deadline = fields.Date(string='Deadline', tracking=True)
    date_closed = fields.Date(string='Closed On', readonly=True, tracking=True)
    is_overdue = fields.Boolean(string='Overdue', compute='_compute_dates', store=True)
    days_open = fields.Integer(string='Days Open', compute='_compute_dates')
    days_to_close = fields.Integer(string='Days to Close', compute='_compute_dates', store=True)

    partner_id = fields.Many2one('res.partner', string='Customer / Supplier', tracking=True, domain="[('is_company', '=', True)]")
    product_id = fields.Many2one('product.product', string='Product', tracking=True)
    lot_id = fields.Many2one('stock.production.lot', string='Lot / Serial Number', tracking=True)
    quantity_affected = fields.Float(string='Affected Quantity', tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UoM')
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id', tracking=True)
    amount_customer = fields.Monetary(string='Final Amount - Customer', currency_field='currency_id', tracking=True)
    amount_sidsa = fields.Monetary(string='Final Amount - SIDSA', currency_field='currency_id', tracking=True)
    amount_supplier = fields.Monetary(string='Final Amount - Supplier', currency_field='currency_id', tracking=True)

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', tracking=True)
    sale_id = fields.Many2one('sale.order', string='Sales Order', tracking=True)
    picking_id = fields.Many2one('stock.picking', string='Picking', tracking=True)
    move_line_id = fields.Many2one('stock.move.line', string='Operation Line', tracking=True)

    description = fields.Text(string='Description / Evidence', tracking=True)
    containment_action = fields.Text(string='Immediate Containment Action', tracking=True)
    root_cause = fields.Text(string='Root Cause Analysis', tracking=True)
    corrective_action = fields.Text(string='Corrective Action', tracking=True)
    preventive_action = fields.Text(string='Preventive Action / Risk Treatment', tracking=True)
    effectiveness_check = fields.Text(string='Effectiveness Check', tracking=True)
    closing_notes = fields.Text(string='Closing Notes', tracking=True)
    environmental_impact = fields.Text(string='Environmental Impact / Controls', tracking=True)

    attachment_count = fields.Integer(string='Attachments', compute='_compute_attachment_count')

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

    @api.constrains('amount_customer', 'amount_sidsa', 'amount_supplier')
    def _check_final_amount_distribution(self):
        for rec in self:
            if not any([rec.amount_customer, rec.amount_sidsa, rec.amount_supplier]):
                raise ValidationError(_('You must define at least one final amount (Customer, SIDSA, or Supplier).'))

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

    def action_open(self):
        self.write({'state': 'open'})

    def action_start_action(self):
        self.write({'state': 'action'})

    def action_verify(self):
        self.write({'state': 'verify'})

    def action_close(self):
        for rec in self:
            missing = []
            if not rec.root_cause:
                missing.append(_('Root Cause Analysis'))
            if not rec.corrective_action:
                missing.append(_('Corrective Action'))
            if rec.state == 'verify' and not rec.effectiveness_check:
                missing.append(_('Effectiveness Check'))
            if missing:
                raise UserError(_('You cannot close the nonconformity until these fields are completed: %s') % ', '.join(missing))
            rec.write({'state': 'done', 'date_closed': fields.Date.context_today(rec)})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft', 'date_closed': False})

    def action_view_attachments(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'context': {'default_res_model': self._name, 'default_res_id': self.id},
        }
