import cv2
import numpy as np

from Core.HookWindow import LocateAllImages, LocateCenterImage, LocateImage, LocateRgbImage, TakeImage


def NumberOfTargets(BattlePosition, Monster):
    print("BPos:",BattlePosition)
    Number = LocateAllImages('images/Targets/Names/' + Monster + '.png', Precision=0.8, Region=(
        BattlePosition[0], BattlePosition[1], BattlePosition[2], BattlePosition[3]))

    if Number > 0:
        return Number
    else:
        return 0


def ScanTarget(BattlePosition, Monster):
    HasTarget = [0, 0]

    HasTarget[0], HasTarget[1] = LocateCenterImage('images/Targets/Names/' + Monster + '.png', Region=(
        BattlePosition[0], BattlePosition[1], BattlePosition[2], BattlePosition[3]), Precision=0.86)

    if HasTarget[0] != 0 and HasTarget[1] != 0:
        if HasTarget[0] < BattlePosition[0]:
            return (BattlePosition[0] - 30) + HasTarget[0] + 1, HasTarget[1] + BattlePosition[1] + 1
        else:
            return (BattlePosition[0] - 40) + HasTarget[0] + 1, HasTarget[1] + BattlePosition[1] + 1
    else:
        return 0, 0

def ScanTarget1(Monster):
    HasTarget = [0, 0]

    #HasTarget[0], HasTarget[1] = LocateCenterImage('images/Targets/Names/' + Monster + '.png', Precision=0.86)
    HasTarget[0], HasTarget[1] = LocateCenterImage('images/Targets/Names/' + Monster + '.png',Precision=0.5)
    if HasTarget[0] != 0 and HasTarget[1] != 0:
        return HasTarget[0], HasTarget[1]
    else:
        return 0, 0        


def CheckWaypoint(image, map_positions):
    wpt = [0, 0]
    middle_start = (map_positions[0] + 48 - 10, map_positions[1] + 48 ) # 23px added in AlexandreCaio Screen because Getters not recnoize the correct posiotion of map
    middle_end = (map_positions[2] - 48, map_positions[3] - 48)
    print("Map Positions:")
    print(map_positions)

    print("middle_start:",middle_start,"  -- middle_end:",middle_end)
    #wpt[0], wpt[1] = LocateRgbImage('images/MapSettings/' + image + '.png', Precision=0.7, Region=(middle_start[0], middle_start[1], middle_end[0], middle_end[1]))
    wpt[0], wpt[1] = LocateCenterImage('images/MapSettings/' + image + '.png',Region=(1765, 65, 1790, 115),Precision=0.60 )
    print("wpt[0]:",wpt[0],"  -- wpt[1]:",wpt[1])
    
    if wpt[0] != 0 and wpt[1] != 0:
        print("Arrived At Mark:", image)
        return True
    else:
        print("Didn't Arrived At Mark:", image)
        return False


def IsAttacking(BattlePosition):
    ImagesAttacking = {
        "LeftRed": False,
        "TopRed": False,
        "RightRed": False,
        "BottomRed": False,

        "LeftBlackRed": False,
        "TopBlackRed": False,
        "RightBlackRed": False,
        "BottomBlackRed": False,

        "LeftPink": False,
        "TopPink": False,
        "RightPink": False,
        "BottomPink": False,

        "LeftBlackPink": False,
        "TopBlackPink": False,
        "RightBlackPink": False,
        "BottomBlackPink": False
    }

    TakedImage = TakeImage(Region=(
        BattlePosition[0], BattlePosition[1], BattlePosition[2], BattlePosition[3]))

    img_rgb = np.array(TakedImage)
    img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)
    #img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    def ScannerAttack(image, Precision=0.8):
        template = cv2.imread(image, 0)
        ''' 1-D Matching    
        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        ''' 
        #3-D Matching
        #res = cv2.matchTemplate(img_rgb[:,:,0], target[:,:,0], cv2.TM_SQDIFF_NORMED )
        res = cv2.matchTemplate(img_rgb[:,:,0], template, cv2.TM_CCOEFF_NORMED )
        '''
        threshold = 0.00001
        loc = np.where( res <= threshold )
        img_rgb = img.copy()
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + 100, pt[1] + 100), (0,0,255), 2)
        ''' 
        min_val, LocatedPrecision, min_loc, Position = cv2.minMaxLoc(res)
        if LocatedPrecision > Precision:
            return False
        return True

    for Image in ImagesAttacking:
        if ScannerAttack('images/MonstersAttack/' + Image + '.png'):
            ImagesAttacking[Image] = True

    if ImagesAttacking['LeftRed'] and ImagesAttacking['TopRed'] and ImagesAttacking['RightRed'] and ImagesAttacking['BottomRed']:
        return True
    elif ImagesAttacking['LeftBlackRed'] and ImagesAttacking['TopBlackRed'] and ImagesAttacking['RightBlackRed'] and ImagesAttacking['BottomBlackRed']:
        return True
    elif ImagesAttacking['LeftPink'] and ImagesAttacking['TopPink'] and ImagesAttacking['RightPink'] and ImagesAttacking['BottomPink']:
        return True
    elif ImagesAttacking['LeftBlackPink'] and ImagesAttacking['TopBlackPink'] and ImagesAttacking['RightBlackPink'] and ImagesAttacking['BottomBlackPink']:
        return True
    else:
        return False


'''X, Y = LocateCenterImage('images/MonstersAttack/top.png', Precision=0.85, Region=(
    BattlePosition[0], BattlePosition[1], BattlePosition[2], BattlePosition[3]))
if X != 0 and Y != 0:
    return True
else:
    X, Y = LocateCenterImage('images/MonstersAttack/right.png', Precision=0.85, Region=(
        BattlePosition[0], BattlePosition[1], BattlePosition[2], BattlePosition[3]))
    if X != 0 and Y != 0:
        return True
    else:
        X, Y = LocateCenterImage('images/MonstersAttack/left.png', Precision=0.85, Region=(
            BattlePosition[0], BattlePosition[1], BattlePosition[2], BattlePosition[3]))
        if X != 0 and Y != 0:
            return True
        else:
            X, Y = LocateCenterImage('images/MonstersAttack/bottom.png', Precision=0.85, Region=(
                BattlePosition[0], BattlePosition[1], BattlePosition[2], BattlePosition[3]))
            if X != 0 and Y != 0:
                return True
            else:
                return False'''


def NeedFollow():
    X, Y = LocateImage('images/TibiaSettings/Idle.png', Precision=0.7)
    if X != 0 and Y != 0:
        return True
    else:
        return False


def NeedIdle():
    X, Y = LocateImage('images/TibiaSettings/Following.png', Precision=0.7)
    if X != 0 and Y != 0:
        return True
    else:
        return False
