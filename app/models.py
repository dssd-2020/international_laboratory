# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _


class Activity(models.Model):
    name = models.CharField(_("Nombre"), max_length=150)

    class Meta:
        verbose_name = _("Actividad")
        verbose_name_plural = _("Actividades")
        ordering = ["-id"]

    def __unicode__(self):
        return u"%s" % self.name

    def __str__(self):
        return self.name


class Protocol(models.Model):
    name = models.CharField(_("Nombre"), max_length=150)
    start_date = models.DateTimeField(_("Fecha de inicio"))
    end_date = models.DateTimeField(_("Fecha de fin"))
    order = models.IntegerField(_("Orden de ejecución"), null=False)
    is_local = models.BooleanField(_("Es local"), default=True)
    points = models.FloatField(_("Puntaje necesario"), null=False)
    activities = models.ManyToManyField(Activity, through='ActivityProtocol', verbose_name="Actividades")

    class Meta:
        verbose_name = _("Protocolo")
        verbose_name_plural = _("Protocolos")
        ordering = ["-id"]

    def __unicode__(self):
        return u"%s" % self.name

    def __str__(self):
        return self.name


class ActivityProtocol(models.Model):
    protocol = models.ForeignKey(Protocol, verbose_name="Protocolo", on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, verbose_name="Actividad", on_delete=models.CASCADE)
    approved = models.BooleanField(_("Aprobado"), default=False)

    class Meta:
        verbose_name = _("Actividad en protocolo")
        verbose_name_plural = _("Actividades en protocolo")

    def __unicode__(self):
        return u"%s en %s" % (self.activity, self.protocol)

    def __str__(self):
        return "{} en {}".format(self.activity, self.protocol)


class Project(models.Model):
    name = models.CharField(_("Nombre"), max_length=150)
    start_date = models.DateTimeField(_("Fecha de inicio"))
    end_date = models.DateTimeField(_("Fecha de fin"))
    project_manager = models.CharField(_("Jefe de proyecto"), max_length=10)
    protocols = models.ManyToManyField(Protocol, through='ProtocolProject', verbose_name="Protocolos")
    active = models.BooleanField(_("Activo"), default=True)
    case_id = models.CharField(_("Número de caso"), max_length=5)
    approved = models.BooleanField(_("Aprobado"), blank=True, null=True)

    class Meta:
        verbose_name = _("Proyecto")
        verbose_name_plural = _("Proyectos")
        ordering = ["-id"]

    def __unicode__(self):
        return u"%s" % self.name

    def __str__(self):
        return self.name


class ProtocolProject(models.Model):
    protocol = models.ForeignKey(Protocol, verbose_name="Protocolo", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name="Proyecto", on_delete=models.CASCADE)
    result = models.FloatField(_("Resultado"), blank=True, null=True)
    approved = models.BooleanField(_("Aprobado"), blank=True, null=True)
    responsible = models.CharField(_("Responsable"), max_length=10)
    running_task = models.CharField(_("Tarea en ejecución"), max_length=10, null=True)

    class Meta:
        verbose_name = _("Protocolo en proyecto")
        verbose_name_plural = _("Protocolo en proyecto")
        ordering = ["approved", "-id"]

    def __unicode__(self):
        return u"%s en %s" % (self.protocol, self.project)

    def __str__(self):
        return "{} en {}".format(self.protocol, self.project)


class Notification(models.Model):
    user_id = models.CharField(_("Destinatario"), max_length=3)
    view = models.BooleanField(_("Leída"), default=False)
    project = models.ForeignKey(Project, verbose_name="Proyecto", on_delete=models.CASCADE)
    protocol = models.ForeignKey(Protocol, verbose_name="Protocolo", blank=True, null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(_("Última modificación"), auto_now=True)

    class Meta:
        verbose_name = _("Notificación")
        verbose_name_plural = _("Notificaciones")
        ordering = ["-updated_at", "-id"]

    def __unicode__(self):
        return u"Notificación para %s" % self.user_id

    def __str__(self):
        return "Notificación para {}".format(self.user_id)

    @property
    def protocol_project(self):
        try:
            return ProtocolProject.objects.get(project=self.project, protocol=self.protocol)
        except ProtocolProject.DoesNotExist:
            return None
