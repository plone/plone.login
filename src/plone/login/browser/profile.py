# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage
from plone.login import MessageFactory as _
from plone.login.interfaces import ICompleteProfile
from plone.z3cform import layout
from z3c.form import button
from z3c.form import field
from z3c.form import form


class CompleteProfileForm(form.EditForm):
    """ Implementation of the complete-profile form """

    fields = field.Fields(ICompleteProfile)
    id = 'CompleteProfileForm'
    label = _(u'heading_complete_profile', default=u'Complete your profile')
    description = _(u'description_complete_profile', default=u'Please provide '
                    u'additional information about yourself.')

    ignoreContext = True

    def getContent(self):
        # XXX: Get member here?
        return self.context

    @button.buttonAndHandler(_(u'button_save', default=u'Save'), name=None)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        IStatusMessage(self.request).addStatusMessage(_(
            u'statusmessage_changes_saved', default=u'Changes saved'
        ), 'info')

    @button.buttonAndHandler(
        _(u'button_cancel', default=u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(
            u'statusmessage_edit_cancelled', default=u'Edit cancelled'
        ), 'info')


class CompleteProfileFormView(layout.FormWrapper):
    form = CompleteProfileForm

    def __init__(self, context, request):
        super(CompleteProfileFormView, self).__init__(context, request)
        self.request['disable_border'] = True
