from common import *
from service.plan import PlanOptimizeService

if __name__ == '__main__':

    new_plan = PlanOptimizeService.optimize_plan_v2(
        subName="瓦屑站", subId="113997367262314836", isYaoKong=True, userNumberWeight=40, lineLoadRateThreshold=80,
        isBusBarRecover=True,
        conclusionText="瓦屑站 事故发生后0条馈线自切至站外不失电，失电用户数8670，通过倒送母线及一级转供恢复2269户用户，通过二级转供及电缆拼接复电0户用户，剩余6401户用户未复电",
        conclusionTwoText="瓦屑站有2台主变、2段母线，厂站最高负载率85.23%；下级馈线可自切至站外馈线0条、直送用户数3条、重要用户进线0条、有转供路径的馈线6条、无转供路径的馈线2条",
        score=-1,
        turn=3)
