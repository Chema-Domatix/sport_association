from odoo import models, fields, api, Command, _
from odoo.exceptions import ValidationError, UserError

class SportIssue(models.Model):
    _name = 'sport.issue'
    _description = 'Sport Issue'
    
    '''def _get_default_user(self):
        return self.env.user'''
    
    name = fields.Char(
        string ='name', 
        required=True) 
    
    description = fields.Text(
        string = 'Description')
    
    date = fields.Date(
        string ='Date')
    
    
    assistance = fields.Boolean(
        string='Assistance',
        help = 'Show if the issue was assisted by medical service')
    
    
    state = fields.Selection(
        string='State',
        selection=[
            ('draft', 'draft'), 
            ('open', 'Open'),
            ('done', 'Done')],
        default = 'draft')
    
    color = fields.Integer(
        string='Color',
        default=0
    )
    
    cost = fields.Float(
        string='Cost',
    )
    
    user_phone = fields.Char(
        string='User Phone',
        related='user_id.phone',
        store = True
    )
    
    user_id = fields.Many2one(
        string='User',
        comodel_name='res.users',
        default=lambda self: self.env.user,
    )
    
    sequence = fields.Integer(
        string='sequence',
        default=10
        
    )
    
    solution = fields.Html(
        string='solution',
    )
    
    assigned = fields.Boolean(
        string='Assigned',
        compute='_compute_assigned',
        inverse = '_inverse_assigned',
        search = '_search_assigned',
        store=True
    )
    
    clinic_id = fields.Many2one(
        string='clinic',
        comodel_name='sport.clinic'
    )
    
    tag_ids = fields.Many2many(
        string='Tag',
        comodel_name='sport.issue.tag'
    ) 
    
    action_ids = fields.One2many(
        string='Action to do',
        comodel_name='sport.issue.action',
        inverse_name='issue_id'
    )
    
    #CONSTRAINS
    @api.constrains('cost')
    def _check_cost(self):
        for record in self:
            if record.cost < 0:
                raise ValidationError(_('Cost cannot be negative')) # dl símbolo _ sirve para indica que se puede traducir. Se debe importar
            
    
    @api.onchange('clinic_id')
    def _onchange_clinic(self):
        for record in self:
            if record.clinic_id:
                record.assistance = True
            else:
                record.assistance = False
                      
                      
    
    @api.depends('user_id')   
    def _compute_assigned(self):
        for record in self:
            record.assigned = bool(record.user_id)
    
    def _inverse_assigned(self):
        for record in self:
            if not record.assigned:
                record.user_id = False
            else:
                record.user_id = self.env.user
    
    def _search_assigned(self, operator, value):
        if operator == '=':
            return [('user_id', operator, value)]
        else:
            return[]
    
    def action_open(self):
        self.ensure_one() #Se usa para asegurarse de que la función solamente se ejecuta sobre un registro
        self.state = 'open'
    
    def action_draft(self):
        self.ensure_one() #Se usa para asegurarse de que la función solamente se ejecuta sobre un registro
        self.state = 'draft'
    
    def action_done(self):
        for record in self:
            if not record.date:
                raise UserError(_('Date is required'))
            self.state = 'done'
    
    def action_add_tag(self):
        for record in self:
            tag_ids = self.env['sport.issue.tag'].search([('name', 'ilike', record.name)])
            if tag_ids:
                record.tag_ids = [Command.set(tag_ids.ids)]
            else:
                record.tag_ids = [Command.create({'name': record.name})]
    
