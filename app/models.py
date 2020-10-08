# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _


# Create your models here.
class Activity(models.Model):
    name = models.CharField(_("Nombre"), max_length=150)

    class Meta:
        verbose_name = _("Actividad")
        verbose_name_plural = _("Actividades")

    def __unicode__(self):
        return u"%s" % self.name

    def __str__(self):
        return self.name


class Member(models.Model):
    first_name = models.CharField(_("Nombre"), max_length=150)
    last_name = models.CharField(_("Apellido"), max_length=150)

    class Meta:
        verbose_name = _("Miembro del equipo")
        verbose_name_plural = _("Miembros del equipo")

    def __unicode__(self):
        return u"%s %s" % self.first_name % self.last_name

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Protocol(models.Model):
    name = models.CharField(_("Nombre"), max_length=150)
    responsible = models.ForeignKey(Member, verbose_name="Responsable", on_delete=models.RESTRICT)
    start_date = models.DateTimeField(_("Fecha de inicio"))
    end_date = models.DateTimeField(_("Fecha de fin"))
    order = models.IntegerField(_("Orden de ejecución"), null=False)
    is_local = models.BooleanField(_("Es local"), default=True)
    points = models.IntegerField(_("Puntaje necesario"), default=0)
    activities = models.ManyToManyField(Activity, through='ActivityProtocol', verbose_name="Actividades")

    class Meta:
        verbose_name = _("Protocolo")
        verbose_name_plural = _("Protocolos")

    def __unicode__(self):
        return u"%s" % self.name

    def __str__(self):
        return self.name


class ActivityProtocol(models.Model):
    protocol = models.ForeignKey(Protocol, verbose_name="Protocolo", on_delete=models.DO_NOTHING())
    activity = models.ForeignKey(Activity, verbose_name="Actividad", on_delete=models.DO_NOTHING())
    result = models.CharField(_("Resultado"), max_length=150)
    approved = models.BooleanField(_("Aprobado"), default=False)

    class Meta:
        verbose_name = _("Actividad en protocolo")
        verbose_name_plural = _("Actividades en protocolo")

    def __unicode__(self):
        return u"%s en %s" % self.activity % self.protocol

    def __str__(self):
        return "{} en {}".format(self.activity, self.protocol)


class Project(models.Model):
    name = models.CharField(_("Nombre"), max_length=150)
    start_date = models.DateTimeField(_("Fecha de inicio"))
    end_date = models.DateTimeField(_("Fecha de fin"))
    project_manager = models.ForeignKey(Member, verbose_name="Jefe de proyecto", on_delete=models.RESTRICT)
    protocols = models.ManyToManyField(Activity, through='ProtocolProject', verbose_name="Protocolos")

    class Meta:
        verbose_name = _("Proyecto")
        verbose_name_plural = _("Proyectos")

    def __unicode__(self):
        return u"%s" % self.name

    def __str__(self):
        return self.name


class ProtocolProject(models.Model):
    protocol = models.ForeignKey(Protocol, verbose_name="Protocolo", on_delete=models.DO_NOTHING())
    project = models.ForeignKey(Project, verbose_name="Proyecto", on_delete=models.DO_NOTHING())
    result = models.CharField(_("Resultado"), max_length=150)
    approved = models.BooleanField(_("Aprobado"), default=False)

    class Meta:
        verbose_name = _("Protocolo en proyecto")
        verbose_name_plural = _("Protocolo en proyecto")

    def __unicode__(self):
        return u"%s en %s" % self.protocol % self.project

    def __str__(self):
        return "{} en {}".format(self.protocol, self.project)
