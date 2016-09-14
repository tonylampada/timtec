# -*- coding: utf-8 -*-
import json

from django.db import models
from jsonfield import JSONField
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Activity(models.Model):
    """
    Generic class to activities
    Data templates (data e type atributes):
    https://github.com/hacklabr/timtec/wiki/Atividades
    Multiple choice
        type: multiplechoice
        data: {question: "", choices: ["choice1", "choice2", ...]}
        expected_answer_data: {choices: [0, 2, 5]} # list of espected choices, zero starting
    Single choice
        type: singlechoice
        data: {question: "", choices: ["choice1", "choice2", ...]}
        expected_answer_data: {choice: 1}
    """
    type = models.CharField(_('Type'), max_length=255)
    data = JSONField(_('Data'), blank=True, null=True)
    expected = JSONField(_('Expected answer'), blank=True, null=True)
    unit = models.ForeignKey('core.Unit', verbose_name=_('Unit'), null=True, blank=True, related_name='activities')
    comment = models.TextField(_('Comment'), blank=True, null=True)
    image = models.ImageField(_('Image'), upload_to='activities', null=True, blank=True)

    class Meta:
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')
        ordering = [('id')]

    def question(self):
        try:
            return self.data.get('question')
        except:
            return None

    def get_image_url(self):
        if self.image:
            return '{}/{}'.format(settings.MEDIA_URL, self.image)
        return ''

    def __unicode__(self):
        return u'%s dt %s a %s' % (self.type, self.data, self.expected)


class Answer(models.Model):
    activity = models.ForeignKey(Activity, verbose_name=_('Activity'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Student'))
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    given = JSONField(_('Given answer'))

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        ordering = ['timestamp']

    @property
    def expected(self):
        if type(self.activity.expected) in [unicode, str]:
            return json.loads(self.activity.expected)
        return self.activity.expected

    def is_correct(self):

        if self.activity.type in ['html5', 'markdown', 'php', 'image']:
            return True

        if type(self.given) is list and type(self.activity.expected) is list:

            if len(self.given) != len(self.activity.expected):
                return False

            for given, expected in zip(self.given, self.activity.expected):
                if isinstance(expected, type(None)) and given not in (None, False,):
                    return False
                elif type(expected) in [int, unicode, str]:
                    try:
                        if type(expected)(given) != expected:
                            return False
                    except:
                        return False
                elif expected is True:
                    try:
                        if bool(given) != expected:
                            return False
                    except:
                        return False
                elif expected is False:
                    if given not in (None, False,):
                        return False

            return True

        result = unicode(self.given) == unicode(self.activity.expected)
        return result
