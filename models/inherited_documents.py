# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sid_nonconformity_ids = fields.One2many('sid.nonconformity', 'purchase_id', string='Nonconformities')
    sid_nonconformity_count = fields.Integer(compute='_compute_sid_nonconformity_count', string='NCs')

    @api.depends('sid_nonconformity_ids')
    def _compute_sid_nonconformity_count(self):
        for rec in self:
            rec.sid_nonconformity_count = len(rec.sid_nonconformity_ids)

    def action_view_sid_nonconformities(self):
        self.ensure_one()
        return self._sid_nc_action([('purchase_id', '=', self.id)], {'default_purchase_id': self.id, 'default_partner_id': self.partner_id.id, 'default_nc_type': 'supplier'})

    def action_create_sid_nonconformity(self):
        self.ensure_one()
        ctx = {
            'default_purchase_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_nc_type': 'supplier',
            'default_title': _('Supplier nonconformity - %s') % (self.name or ''),
        }
        return self._sid_nc_form_action(ctx)

    def _sid_nc_action(self, domain, context):
        action = self.env.ref('sid_nonconformity.action_sid_nonconformity').read()[0]
        action['domain'] = domain
        action['context'] = context
        return action

    def _sid_nc_form_action(self, context):
        return {
            'name': _('New Nonconformity'),
            'type': 'ir.actions.act_window',
            'res_model': 'sid.nonconformity',
            'view_mode': 'form',
            'target': 'current',
            'context': context,
        }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sid_nonconformity_ids = fields.One2many('sid.nonconformity', 'sale_id', string='Nonconformities')
    sid_nonconformity_count = fields.Integer(compute='_compute_sid_nonconformity_count', string='NCs')

    @api.depends('sid_nonconformity_ids')
    def _compute_sid_nonconformity_count(self):
        for rec in self:
            rec.sid_nonconformity_count = len(rec.sid_nonconformity_ids)

    def action_view_sid_nonconformities(self):
        self.ensure_one()
        return self._sid_nc_action([('sale_id', '=', self.id)], {'default_sale_id': self.id, 'default_partner_id': self.partner_id.id, 'default_nc_type': 'customer'})

    def action_create_sid_nonconformity(self):
        self.ensure_one()
        ctx = {
            'default_sale_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_nc_type': 'customer',
            'default_title': _('Customer nonconformity - %s') % (self.name or ''),
        }
        return self._sid_nc_form_action(ctx)

    def _sid_nc_action(self, domain, context):
        action = self.env.ref('sid_nonconformity.action_sid_nonconformity').read()[0]
        action['domain'] = domain
        action['context'] = context
        return action

    def _sid_nc_form_action(self, context):
        return {
            'name': _('New Nonconformity'),
            'type': 'ir.actions.act_window',
            'res_model': 'sid.nonconformity',
            'view_mode': 'form',
            'target': 'current',
            'context': context,
        }


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sid_nonconformity_ids = fields.One2many('sid.nonconformity', 'picking_id', string='Nonconformities')
    sid_nonconformity_count = fields.Integer(compute='_compute_sid_nonconformity_count', string='NCs')

    @api.depends('sid_nonconformity_ids')
    def _compute_sid_nonconformity_count(self):
        for rec in self:
            rec.sid_nonconformity_count = len(rec.sid_nonconformity_ids)

    def action_view_sid_nonconformities(self):
        self.ensure_one()
        return self._sid_nc_action([('picking_id', '=', self.id)], {'default_picking_id': self.id, 'default_partner_id': self.partner_id.id, 'default_nc_type': 'warehouse'})

    def action_create_sid_nonconformity(self):
        self.ensure_one()
        ctx = {
            'default_picking_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_nc_type': 'warehouse',
            'default_title': _('Logistics nonconformity - %s') % (self.name or ''),
        }
        return self._sid_nc_form_action(ctx)

    def _sid_nc_action(self, domain, context):
        action = self.env.ref('sid_nonconformity.action_sid_nonconformity').read()[0]
        action['domain'] = domain
        action['context'] = context
        return action

    def _sid_nc_form_action(self, context):
        return {
            'name': _('New Nonconformity'),
            'type': 'ir.actions.act_window',
            'res_model': 'sid.nonconformity',
            'view_mode': 'form',
            'target': 'current',
            'context': context,
        }
