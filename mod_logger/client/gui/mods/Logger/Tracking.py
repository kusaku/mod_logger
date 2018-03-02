from datetime import datetime

import BigWorld

import GUI
from Account import g_accountRepository
from Event import Event
from PlayerEvents import g_playerEvents
from ReplayEvents import g_replayEvents
from collections import OrderedDict, defaultdict
from game import g_onBeforeSendEvent, g_replayCtrl
from gui.InputHandler import g_instance
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE, SHELL_SET_RESULT
from gui.mods.Logger import LOG_DEBUG, UPDATE_GUI_INTERVAL
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from messenger.proto.events import g_messengerEvents
from skeletons.gui.battle_session import IBattleSessionProvider


class Tracking(CallbackDelayer):
    def __debug(self, *args):
        entry = (datetime.now().strftime('%H:%M:%S.%f'),) + args
        while len(self.__console) > 40:
            del self.__console[0]
        if len(self.__console) == 0 or entry[1] != self.__console[-1][1]:
            self.__console.append(entry)
        LOG_DEBUG(*args)

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__statdata = OrderedDict()
        self.__console = list()
        self.__trackers = dict()
        self.__shell_qauntity = defaultdict(int)
        self.__gui = GUI.Text()
        self.__gui.position = (-1, -1, 0)
        self.__gui.horizontalAnchor = 'LEFT'
        self.__gui.verticalAnchor = 'BOTTOM'
        self.__gui.colourFormatting = True
        self.__gui.multiline = True
        self.__gui.font = 'default_small.font'

    def __get_events(self, name, ctrl):
        return {name + '.' + prop: getattr(ctrl, prop) for prop in dir(ctrl) if
                prop.startswith('on') and isinstance(getattr(ctrl, prop), Event)}

    def __get_global_events(self):
        return (
            self.__get_events('g_accountRepository', g_accountRepository),
            self.__get_events('g_messengerEvents', g_messengerEvents),
            self.__get_events('g_playerEvents', g_playerEvents),
            self.__get_events('g_replayEvents', g_replayEvents),
            self.__get_events('g_replayCtrl', g_replayCtrl),
            self.__get_events('g_instance', g_instance),
            # {'g_onBeforeSendEvent': g_onBeforeSendEvent}
        )

    def __get_battle_events(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        return (
            self.__get_events('player', BigWorld.player()),
            self.__get_events('arena', BigWorld.player().arena),
            self.__get_events('ammo', sessionProvider.shared.ammo),
            self.__get_events('equipments', sessionProvider.shared.equipments),
            self.__get_events('optionalDevices', sessionProvider.shared.optionalDevices),
            self.__get_events('vehicleState', sessionProvider.shared.vehicleState),
            self.__get_events('hitDirection', sessionProvider.shared.hitDirection),
            self.__get_events('arenaLoad', sessionProvider.shared.arenaLoad),
            self.__get_events('arenaPeriod', sessionProvider.shared.arenaPeriod),
            self.__get_events('feedback', sessionProvider.shared.feedback),
            self.__get_events('chatCommands', sessionProvider.shared.chatCommands),
            self.__get_events('messages', sessionProvider.shared.messages),
            self.__get_events('drrScale', sessionProvider.shared.drrScale),
            self.__get_events('privateStats', sessionProvider.shared.privateStats),
            self.__get_events('crosshair', sessionProvider.shared.crosshair),
            self.__get_events('personalEfficiencyCtrl', sessionProvider.shared.personalEfficiencyCtrl),
            self.__get_events('battleCacheCtrl', sessionProvider.shared.battleCacheCtrl),
            self.__get_events('viewPoints', sessionProvider.shared.viewPoints),
            self.__get_events('debug', sessionProvider.dynamic.debug),
            self.__get_events('teamBases', sessionProvider.dynamic.teamBases),
            self.__get_events('respawn', sessionProvider.dynamic.respawn),
            self.__get_events('dynSquads', sessionProvider.dynamic.dynSquads),
            self.__get_events('gasAttack', sessionProvider.dynamic.gasAttack),
            self.__get_events('battleField', sessionProvider.dynamic.battleField),
            self.__get_events('playerGameModeData', sessionProvider.dynamic.playerGameModeData),
            self.__get_events('teamHealthBar', sessionProvider.dynamic.teamHealthBar)
        )

    def __track(self, type, *args, **kwargs):
        if type == 'arena.onPositionUpdated':
            return

        if type == 'vehicleState.onVehicleStateUpdated':
            state = {
                1: 'FIRE',
                2: 'DEVICES',
                4: 'HEALTH',
                8: 'DESTROYED',
                16: 'CREW_DEACTIVATED',
                32: 'AUTO_ROTATION',
                64: 'SPEED',
                128: 'CRUISE_MODE',
                256: 'REPAIRING',
                512: 'PLAYER_INFO',
                1024: 'SHOW_DESTROY_TIMER',
                2048: 'HIDE_DESTROY_TIMER',
                4096: 'OBSERVED_BY_ENEMY',
                8192: 'RESPAWNING',
                16384: 'SWITCHING',
                32768: 'SHOW_DEATHZONE_TIMER',
                65536: 'HIDE_DEATHZONE_TIMER',
                131072: 'MAX_SPEED',
                262144: 'RPM',
                524288: 'VEHICLE_ENGINE_STATE',
                1048576: 'VEHICLE_MOVEMENT_STATE',
                2097152: 'DEATH_INFO',
                4194304: 'VEHICLE_CHANGED',
                8388608: 'SIEGE_MODE',
                16777216: 'STUN'
            }.get(args[0])

            self.__debug(type, state, *args, **kwargs)

        elif type == 'feedback.onVehicleFeedbackReceived':

            state = {
                1: 'PLAYER_KILLED_ENEMY',
                2: 'PLAYER_DAMAGED_HP_ENEMY',
                3: 'PLAYER_DAMAGED_DEVICE_ENEMY',
                4: 'PLAYER_SPOTTED_ENEMY',
                5: 'PLAYER_ASSIST_TO_KILL_ENEMY',
                6: 'PLAYER_ASSIST_TO_STUN_ENEMY',
                7: 'PLAYER_USED_ARMOR',
                8: 'PLAYER_CAPTURED_BASE',
                9: 'PLAYER_DROPPED_CAPTURE',
                10: 'VEHICLE_HEALTH',
                11: 'VEHICLE_HIT',
                12: 'VEHICLE_CRITICAL_HIT',
                13: 'VEHICLE_CRITICAL_HIT_DAMAGE',
                14: 'VEHICLE_CRITICAL_HIT_CHASSIS',
                15: 'VEHICLE_RICOCHET',
                16: 'VEHICLE_ARMOR_PIERCED',
                17: 'VEHICLE_DEAD',
                18: 'VEHICLE_SHOW_MARKER',
                19: 'VEHICLE_ATTRS_CHANGED',
                20: 'VEHICLE_IN_FOCUS',
                21: 'VEHICLE_HAS_AMMO',
                22: 'SHOW_VEHICLE_DAMAGES_DEVICES',
                23: 'HIDE_VEHICLE_DAMAGES_DEVICES',
                24: 'MINIMAP_SHOW_MARKER',
                25: 'MINIMAP_MARK_CELL',
                26: 'DAMAGE_LOG_SUMMARY',
                27: 'POSTMORTEM_SUMMARY',
                28: 'ENEMY_DAMAGED_HP_PLAYER',
                29: 'ENEMY_DAMAGED_DEVICE_PLAYER',
                30: 'VEHICLE_VISIBILITY_CHANGED',
                31: 'VEHICLE_STUN'
            }.get(args[0])

            if state in [
                'VEHICLE_HIT',
                'VEHICLE_ARMOR_PIERCED',
            ]:
                if self.__statdata.has_key(state):
                    self.__statdata[state] += 1
                else:
                    self.__statdata[state] = 1

            self.__debug(type, state, *args, **kwargs)

        elif type == 'feedback.onPlayerFeedbackReceived':
            states = [{
                          1: 'PLAYER_KILLED_ENEMY',
                          2: 'PLAYER_DAMAGED_HP_ENEMY',
                          3: 'PLAYER_DAMAGED_DEVICE_ENEMY',
                          4: 'PLAYER_SPOTTED_ENEMY',
                          5: 'PLAYER_ASSIST_TO_KILL_ENEMY',
                          6: 'PLAYER_USED_ARMOR',
                          7: 'PLAYER_CAPTURED_BASE',
                          8: 'PLAYER_DROPPED_CAPTURE',
                          9: 'VEHICLE_HEALTH',
                          10: 'VEHICLE_HIT',
                          11: 'VEHICLE_ARMOR_PIERCED',
                          12: 'VEHICLE_DEAD',
                          13: 'VEHICLE_SHOW_MARKER',
                          14: 'VEHICLE_ATTRS_CHANGED',
                          15: 'VEHICLE_IN_FOCUS',
                          16: 'VEHICLE_HAS_AMMO',
                          17: 'SHOW_VEHICLE_DAMAGES_DEVICES',
                          18: 'HIDE_VEHICLE_DAMAGES_DEVICES',
                          19: 'MINIMAP_SHOW_MARKER',
                          20: 'MINIMAP_MARK_CELL',
                          21: 'DAMAGE_LOG_SUMMARY',
                          22: 'POSTMORTEM_SUMMARY',
                          23: 'ENEMY_DAMAGED_HP_PLAYER',
                          24: 'ENEMY_DAMAGED_DEVICE_PLAYER',
                      }.get(a.getType()) for a in args[0]]

            for state in states:
                if state in [
                    'PLAYER_KILLED_ENEMY',
                    'PLAYER_DAMAGED_HP_ENEMY',
                    'PLAYER_DAMAGED_DEVICE_ENEMY',
                    'PLAYER_SPOTTED_ENEMY',
                    'PLAYER_ASSIST_TO_KILL_ENEMY',
                    'PLAYER_USED_ARMOR',
                    'PLAYER_CAPTURED_BASE',
                    'PLAYER_DROPPED_CAPTURE',
                    'ENEMY_DAMAGED_HP_PLAYER',
                    'ENEMY_DAMAGED_DEVICE_PLAYER',
                ]:
                    if self.__statdata.has_key(state):
                        self.__statdata[state] += 1
                    else:
                        self.__statdata[state] = 1

            self.__debug(type, states, *args, **kwargs)

        else:
            self.__debug(type, *args, **kwargs)

        if type == 'personalEfficiencyCtrl.onTotalEfficiencyUpdated':
            sessionProvider = dependency.instance(IBattleSessionProvider)
            self.__statdata['DAMAGE'] = sessionProvider.shared.personalEfficiencyCtrl.getTotalEfficiency(
                PERSONAL_EFFICIENCY_TYPE.DAMAGE)
            self.__statdata['BLOCKED_DAMAGE'] = sessionProvider.shared.personalEfficiencyCtrl.getTotalEfficiency(
                PERSONAL_EFFICIENCY_TYPE.BLOCKED_DAMAGE)
            self.__statdata['ASSIST_DAMAGE'] = sessionProvider.shared.personalEfficiencyCtrl.getTotalEfficiency(
                PERSONAL_EFFICIENCY_TYPE.ASSIST_DAMAGE)

        if type == 'arena.onVehicleStatisticsUpdate':
            self.__debug(repr(BigWorld.player().arena.statistics))

        if type == 'ammo.onShellsAdded':
            intCD, descriptor, quantity, quantityInClip, gunSettings = args
            self.__shell_qauntity[intCD] = quantity

        if type == 'ammo.onShellsUpdated':
            intCD, quantity, quantityInClip, result = args
            shots_made = self.__shell_qauntity[intCD] - quantity
            self.__shell_qauntity[intCD] = quantity
            if result & SHELL_SET_RESULT.CURRENT:
                if self.__statdata.has_key('SHOTS'):
                    self.__statdata['SHOTS'] += shots_made
                else:
                    self.__statdata['SHOTS'] = shots_made

    def __get_tracker(self, type):
        return self.__trackers.setdefault(type, lambda *args, **kwargs: self.__track(type, *args, **kwargs))

    def __update_gui(self):
        self.__gui.text = ''.join(
            map(lambda a: '\cFFFFFF80;%s: \cFF800080;%s\n' % (a[0], ' '.join(map(repr, a[1:]))), self.__console))

        if self.__gui.parent is None:
            GUI.roots()[-1].addChild(self.__gui)
        elif self.__gui.parent not in GUI.roots():
            self.__gui.parent.delChild(self.__gui)

        return UPDATE_GUI_INTERVAL

    def __onAvatarBecomePlayer(self):
        self.__statdata = OrderedDict()

        for ctrl_event in self.__get_battle_events():
            for name, event in ctrl_event.iteritems():
                # self.__debug('bound to %s' % name)
                event += self.__get_tracker(name)

    def __onAvatarBecomeNonPlayer(self):
        for stat_name, stat_value in self.__statdata.iteritems():
            self.__debug('%s: %d' % (stat_name, stat_value))

        for ctrl_event in self.__get_battle_events():
            for name, event in ctrl_event.iteritems():
                # self.__debug('unbound from %s' % name)
                event -= self.__get_tracker(name)

    def init(self):
        for ctrl_event in self.__get_global_events():
            for name, event in ctrl_event.iteritems():
                # self.__debug('bound to %s' % name)
                event += self.__get_tracker(name)

        g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer

        # self.delayCallback(UPDATE_GUI_INTERVAL, self.__update_gui)

    def fini(self):
        for ctrl_event in self.__get_global_events():
            for name, event in ctrl_event.iteritems():
                # self.__debug('bound to %s' % name)
                event -= self.__get_tracker(name)

        g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer

        # self.stopCallback(self.__update_gui)


g_loggerTracking = Tracking()
