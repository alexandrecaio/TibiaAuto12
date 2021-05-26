import json
from time import sleep, time

from Conf.Hotkeys import Hotkey
#MODULARIZAR MELHOR DEPOIS
#from Core.HookWindow import LocateCenterImage
from Core.HookWindow import LocateCenterImage, LocateRgbImage
import cv2
import numpy as np
#FIM MODULARIZACAO
from Engine.CaveBot.Scanners import NumberOfTargets, ScanTarget, IsAttacking, NeedFollow, CheckWaypoint

TargetNumber = 0
NumberOfMonster = []


class CaveBotController:
    def __init__(self, MOUSE_OPTION, ScriptName, LootButton, TimeToStand, Walk, Loot, ForRefresh, MapPosition, BattlePosition, SQMs):
        self.MOUSE_OPTION = MOUSE_OPTION
        self.SendToClient = Hotkey(self.MOUSE_OPTION)
        self.ScriptName = ScriptName
        self.LootButton = LootButton
        self.TimeToStand = TimeToStand
        self.EnabledWalk = Walk
        self.EnabledLooting = Loot
        self.WalkForRefresh = ForRefresh
        self.MapPosition = MapPosition
        self.BattlePosition = BattlePosition
        self.SQMs = SQMs
        self.Target = []

        # Remember Set For Get From Cavebot (for me)

        self.FollowMode = True

    '''
    StartCaveBot Take The Data From Module CaveBot And Search For Mark With Status TRUE,
    When He Finds, He Starts The Engine Of CaveBot.
    '''

    def StartCaveBot(self, data, MonstersToAttack):
        while IsEnable():
            for i in range(len(data)):
                if not IsEnable():
                    return
                else:
                    if data[i]['status']:
                        self.HandleCaveBot(data, i, MonstersToAttack)

    '''
    The Handler 
    '''

    def HandleCaveBot(self, data, i, Monsters):

        global TargetNumber
        MarkLocation = [0, 0]

        sleep(self.TimeToStand)

        if not IsEnable():
            return

        '''
        Disconsider This Block If You Don't Mark The Walk Option...
        '''
        # region Walk

        if self.EnabledWalk:
            while MarkLocation[0] == 0 and MarkLocation[1] == 0:
                MarkLocation[0], MarkLocation[1] = LocateCenterImage('images/MapSettings/' + data[i]["mark"] + '.png',
                                                 Region=(
                                                     self.MapPosition[0], self.MapPosition[1], self.MapPosition[2],
                                                     self.MapPosition[3]),
                                                 Precision=0.8)
                if MarkLocation[0] == 0 and MarkLocation[1] == 0:
                    print("Mark: { ", data[i]["mark"], " } Not Located, Try Again")
                    if self.WalkForRefresh:
                        sleep(.3)
                        self.SendToClient.Press('up_arrow')
                        sleep(.1)
                        self.SendToClient.Press('left_arrow')
                        sleep(.7)
                        self.SendToClient.Press('down_arrow')
                        sleep(.1)
                        self.SendToClient.Press('right_arrow')
                        sleep(.1)
                else:
                    print("successfully Located The Mark: { ", data[i]["mark"], " } Clicking On Your Position")
                    MarkLocation[0] = self.MapPosition[0] + MarkLocation[0]
                    MarkLocation[1] = self.MapPosition[1] + MarkLocation[1]

            # Clicking In Mark Position

            if self.MOUSE_OPTION == 1:
                PastPosition = self.SendToClient.Position()
            else:
                PastPosition = [0, 0]

            self.SendToClient.LeftClick(MarkLocation[0], MarkLocation[1])

            if self.MOUSE_OPTION == 1:
                self.SendToClient.MoveTo(PastPosition[0], PastPosition[1])

        # endregion

        '''
        The Attack, Is Every Time Enabled.
        '''

        # region Attack

        for Monster in Monsters:

            FirstMonstersNumber = 0
            SecondMonstersNumber = 0

            Number = NumberOfTargets(self.BattlePosition, Monster)
            # NumberOfMonster.append(Number)

            while Number > 0:

                if not IsEnable():
                    return

                self.Target = ScanTarget(self.BattlePosition, Monster)

                if self.Target[0] != 0 and self.Target[1] != 0:

                    # Verify If You Are Already Attacking !
                    if IsAttacking(self.BattlePosition):
                        print("Attacking The Target")

                        if self.MOUSE_OPTION == 1:
                            PastPosition = self.SendToClient.Position()
                        else:
                            PastPosition = [0, 0]

                        self.SendToClient.LeftClick(self.Target[0], self.Target[1])

                        if self.MOUSE_OPTION == 1:
                            self.SendToClient.MoveTo(PastPosition[0], PastPosition[1])

                        FirstMonstersNumber = NumberOfTargets(self.BattlePosition, Monster)
                    else:
                        print("You are attacking")
                        FirstMonstersNumber = NumberOfTargets(self.BattlePosition, Monster)

                # Control Follow Mode In Attack (Follow Or Idle)

                if self.FollowMode:

                    IsNeedFollow = NeedFollow()

                    if IsNeedFollow:
                        print("Clicking In Follow")

                        if self.MOUSE_OPTION == 1:
                            PastPosition = self.SendToClient.Position()
                        else:
                            PastPosition = [0, 0]
                        FollowPosition = LocateCenterImage('images/TibiaSettings/NotFollow.png', Precision=0.7)
                        self.SendToClient.LeftClick(FollowPosition[0], FollowPosition[1])
                        if self.MOUSE_OPTION == 1:
                            self.SendToClient.MoveTo(PastPosition[0], PastPosition[1])

                sleep(.2)

                self.Target = ScanTarget(self.BattlePosition, Monster)

                if self.Target[0] != 0 and self.Target[1] != 0:

                    # Verify If You Are Already Attacking !
                    if IsAttacking(self.BattlePosition):
                        # For Debugging
                        # print("Attacking The Target2")

                        if self.MOUSE_OPTION == 1:
                            PastPosition = self.SendToClient.Position()
                        else:
                            PastPosition = [0, 0]

                        self.SendToClient.LeftClick(self.Target[0], self.Target[1])

                        if self.MOUSE_OPTION == 1:
                            self.SendToClient.MoveTo(PastPosition[0], PastPosition[1])

                        SecondMonstersNumber = NumberOfTargets(self.BattlePosition, Monster)
                    else:
                        # For Debugging
                        # print("You are attacking2")

                        SecondMonstersNumber = NumberOfTargets(self.BattlePosition, Monster)

                if SecondMonstersNumber < FirstMonstersNumber:
                    self.TakeLoot()

                self.Target = []

                sleep(0.2)

                Number = NumberOfTargets(self.BattlePosition, Monster)

                if Number == 0:
                    break

        '''
            If Walk Option Is Enabled, It Verify If The Player Already
            Arrived To The Current Mark.
            
            If Already Arrived, It Set On Script, The Current Mark As False
            And The Next Mark As True, For The Next Check.
        '''

        if self.EnabledWalk:
            if CheckWaypoint(data[i]["mark"], self.MapPosition):
                data[i]['status'] = False
                if i + 1 == len(data):
                    data[i - i]['status'] = True
                    with open('Scripts/' + self.ScriptName + '.json', 'w') as wJson:
                        json.dump(data, wJson, indent=4)
                else:
                    data[i + 1]['status'] = True
                    with open('Scripts/' + self.ScriptName + '.json', 'w') as wJson:
                        json.dump(data, wJson, indent=4)
            else:
                self.HandleCaveBot(data, i, Monsters)

        # endregion

    '''
        Clicking Around Of The Player To Get A Loot.
    '''
    '''
    def TakeLoot(self):
        if self.MOUSE_OPTION == 1:
            PastPosition = self.SendToClient.Position()
        else:
            PastPosition = [0, 0]

        # For Debugging
        # StartLootTime = time()

        for i, j in zip(range(0, 18, + 2), range(1, 19, + 2)):
            if self.LootButton == 'right':
                #self.SendToClient.RightClick(self.SQMs[i], self.SQMs[j])
                self.SendToClient.RightClick(self.SQMs[i]-90, self.SQMs[j])
                sleep(.3)
            elif self.LootButton == 'left':
                self.SendToClient.LeftClick(self.SQMs[i], self.SQMs[j])

        # For Debugging
        # EndLootTime = time() - StartLootTime

        if self.MOUSE_OPTION == 1:
            self.SendToClient.MoveTo(PastPosition[0], PastPosition[1])

        # For Debugging
        # print("Looted In: ", EndLootTime)
    '''
    def TakeLoot(self):
        if self.MOUSE_OPTION == 1:
            PastPosition = self.SendToClient.Position()
        else:
            PastPosition = [0, 0]

        # For Debugging
        # StartLootTime = time()

       # for i, j in zip(range(0, 18, + 2), range(1, 19, + 2)):
       #     if self.LootButton == 'right':
                #self.SendToClient.RightClick(self.SQMs[i], self.SQMs[j])
       #         self.SendToClient.RightClick(self.SQMs[i]-90, self.SQMs[j])
       #         sleep(.3)
       #     elif self.LootButton == 'left':
       #         self.SendToClient.LeftClick(self.SQMs[i], self.SQMs[j])

        for i in range(1, 10):
            if self.LootButton == 'right':
                if i==1:
                    self.SendToClient.RightClick(806, 535)
                elif i==2:
                    self.SendToClient.RightClick(874, 540)
                elif i==3:
                    self.SendToClient.RightClick(950, 535)
                elif i==4:
                    self.SendToClient.RightClick(790, 470)
                elif i==5:
                    self.SendToClient.RightClick(870, 482)
                elif i==6:
                    self.SendToClient.RightClick(930, 480)
                elif i==7:
                    self.SendToClient.RightClick(782, 400)
                elif i==8:
                    self.SendToClient.RightClick(867, 400)
                elif i==9:
                    self.SendToClient.RightClick(949, 400)
                #else:
                #    nome = None
                #    print "Valor invalido"
                #self.SendToClient.RightClick(self.SQMs[i], self.SQMs[j])
                #
                #self.SendToClient.RightClick(self.SQMs[i]-90, self.SQMs[j])
                sleep(.17)
            elif self.LootButton == 'left':
                self.SendToClient.LeftClick(self.SQMs[i], self.SQMs[j])

        # For Debugging
        # EndLootTime = time() - StartLootTime

        

        # For Debugging
        # print("Looted In: ", EndLootTime)
        #loc = pyautogui.locateOnScreen(bpname+".png") 'images/LootableItens/' + Image + '.png')
        lootitems = ['SmallStone','SmallStone2','SmallStone3']
        '''
        pyautogui.moveTo(783, 320+32) #DEFAULT FULL SCREEN IS +23 - NOW I DID IT 32
        pyautogui.click(button='right')
        sleep(1)
        pyautogui.moveTo(827, 316+32) #DEFAULT FULL SCREEN IS +23 - NOW I DID IT 32
        pyautogui.click(button='right')
        pyautogui.moveTo(827+500, 316+32) #DEFAULT FULL SCREEN IS +23 - NOW I DID IT 32
        '''
        '''
        w.RightClick((453,280+32))
        sleep(0.5)
        w.RightClick((500,280))
        sleep(0.5)
        w.RightClick((544,280))
        sleep(0.5)
        w.RightClick((461,325))
        sleep(0.5)
        w.RightClick((462,362))
        sleep(0.5)
        w.RightClick((507,365))
        sleep(0.5)
        w.RightClick((544,368))
        sleep(0.5)
        w.RightClick((548,322))
        sleep(1)
        '''
        #TakedImage = TakeImage(Region=(1739, 950, 1916, 1022))
        #img_rgb = np.array(TakedImage)
        #count = len(lootitems)
        
        for image in lootitems:
            wpt = [0, 0]
            #template = cv2.imread('images/LootableItens/' + image + '.png', 0)
            wpt[0], wpt[1] = LocateRgbImage('images/LootableItens/' + image + '.png', Precision=0.7, Region=(2, 950, 1916, 1022))
            #res = cv2.matchTemplate(img_rgb[:,:,0], template, cv2.TM_CCOEFF_NORMED )
            '''
            threshold = 0.00001
            loc = np.where( res <= threshold )
            img_rgb = img.copy()
            for pt in zip(*loc[::-1]):
                cv2.rectangle(img_rgb, pt, (pt[0] + 100, pt[1] + 100), (0,0,255), 2)
            ''' 
            if (wpt[0]!=0 and wpt[1]!= 0 ):
                #self.SendToClient.MoveTo(1739+wpt[0]+18,950+wpt[1]+15)
                #sleep(3)
                #self.SendToClient.MoveTo(1844,170)
                #sleep(3)
                #self.SendToClient.DragTo((1739+wpt[0]+18,15+950+wpt[1]),(1739+wpt[0]+18,15+850+wpt[1]))
                self.SendToClient.DragTo((2+wpt[0]+18,15+950+wpt[1]),(1790+18,850))
            '''
                self.SendToClient.MoveTo(1739+wpt[0],950+wpt[1])
                sleep(3)
                self.SendToClient.MoveTo(1844,170)
                sleep(3)
                self.SendToClient.DragTo((1739+wpt[0]+14,14+950+wpt[1]),(1844,120))
            '''
            #gold = pyautogui.locateAllOnScreen(lootitems[i]+'.png', confidence=.9, region=(1196,422, 1368, 726))
            #for item in gold:
            #    self.SendToClient.DragTo()
            #    #w.MouseDrag((item.left,item.top),(loc.left,(loc.top+20)))
            #    sleep(1)
        wpt = [0, 0]
        #template = cv2.imread('images/LootableItens/' + image + '.png', 0)
        wpt[0], wpt[1] = LocateRgbImage('images/LootableItens/Fish.png', Precision=0.7, Region=(1739, 950, 1916, 1022))
        sleep(.17)
        if (wpt[0]!=0 and wpt[1]!= 0 ):
            self.SendToClient.MoveTo(wpt[0], wpt[1]) 
            sleep(3)
        if self.MOUSE_OPTION == 1:
            self.SendToClient.MoveTo(PastPosition[0], PastPosition[1])   
'''
    Import The EnabledCaveBot Variable From CaveBot Module, To Verify
    If CaveBot Is Enabled.
'''


def IsEnable():
    from Modules.CaveBot import EnabledCaveBot
    return EnabledCaveBot
