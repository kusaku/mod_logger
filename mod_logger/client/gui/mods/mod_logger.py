#
# mod_logger entry point
#

from gui.mods.Logger import LOG_DEBUG
from gui.mods.Logger.Tracking import g_loggerTracking


def init():
    LOG_DEBUG('init')
    g_loggerTracking.init()


def fini():
    LOG_DEBUG('fini')
    g_loggerTracking.fini()


def onAccountBecomeNonPlayer():
    LOG_DEBUG('onAccountBecomeNonPlayer')


def onAccountBecomePlayer():
    LOG_DEBUG('onAccountBecomePlayer')


def onAccountShowGUI(ctx):
    LOG_DEBUG('onAccountShowGUI', ctx)


def onAvatarBecomePlayerdef():
    LOG_DEBUG('onAvatarBecomePlayerdef')
