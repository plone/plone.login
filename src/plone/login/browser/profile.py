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
    id = "CompleteProfileForm"
    label = _(u"Complete your profile")
    description = _(u"Please provide additional information about yourself.")

    ignoreContext = True

    def getContent(self):
        # XXX: Get member here?
        return self.context

    @button.buttonAndHandler(_('Save'), name=None)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        #self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                      "info")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")

class CompleteProfileFormView(layout.FormWrapper):
    form = CompleteProfileForm

    def __init__(self, context, request):
        super(CompleteProfileFormView, self).__init__(context, request)
        self.request['disable_border'] = True
