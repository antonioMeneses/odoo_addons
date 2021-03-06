# -*- coding: utf-8 -*-
# (C) 2013 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAssetHistory(models.Model):
    _name = 'account.asset.history'
    _description = 'Asset history'
    _inherit = 'abstract.asset'
    _rec_name = 'asset_id'
    _order = 'date_to desc'

    date_to = fields.Datetime(
        'Until', readonly=True, default=fields.Datetime.now)
    user_id = fields.Many2one(
        'res.users', 'User', readonly=True, ondelete='restrict',
        default=lambda self: self._uid)
    asset_id = fields.Many2one(
        'account.asset.asset', 'Asset',
        required=True, ondelete='cascade', index=True, auto_join=True)
    category_id = fields.Many2one(
        'account.asset.category', 'Asset Category',
        required=True, ondelete='restrict')
    company_id = fields.Many2one(
        related='asset_id.company_id', readonly=True)
    currency_id = fields.Many2one(
        related='asset_id.currency_id', readonly=True)
    purchase_value = fields.Monetary('Gross Value', required=True)
    salvage_value = fields.Monetary('Salvage Value')
    purchase_tax_amount = fields.Monetary('Tax Amount', readonly=True)
    purchase_date = fields.Date(required=True, readonly=True)
    in_service_date = fields.Date('In-service Date')
    benefit_accelerated_depreciation = fields.Boolean(readonly=True)
    note = fields.Text('Reason')

    @api.model
    def _get_fields_to_read(self):
        return list(set(self._fields.keys()) - set(models.MAGIC_COLUMNS)
                    & set(self.env['account.asset.asset']._fields.keys())
                    - {'old_id', '__last_update'})

    @api.onchange('asset_id')
    def _onchange_asset(self):
        for field in self._get_fields_to_read():
            self[field] = self.asset_id[field]

    @api.onchange('category_id')
    def _onchange_category(self):
        for field in self.asset_id._category_fields:
            self[field] = self.category_id[field]

    @api.model
    def create(self, vals):
        if self._context.get('data_integration'):
            return super(AccountAssetHistory, self).create(vals)
        # Update asset with vals and save old vals by creating a history record
        asset = self.env['account.asset.asset'].browse(vals['asset_id'])
        fields_to_read = self._get_fields_to_read()
        old_vals = asset.read(fields_to_read, load='_classic_write')[0]
        del old_vals['id']
        for field in dict(vals):
            if field not in fields_to_read:
                old_vals[field] = vals[field]
                del vals[field]
        asset.write(vals)
        asset.compute_depreciation_board()
        return super(AccountAssetHistory, self).create(old_vals)

    @api.multi
    def validate(self):
        if self._context.get('asset_validation'):
            self.mapped('asset_id').validate()
        return True

    @api.multi
    def button_validate(self):
        self.validate()
        return {'type': 'ir.actions.act_window_close'}
