from service.plan import *

if __name__ == '__main__':
    subId = "113997367262314626"
    isYaoKong = True
    userNumberWeight = 0
    lineLoadRateThreshold = 80
    isBusBarRecover = True
    busbarNotRepeatLineList = [
        {
            'oppositeLineName': '创37康新',
            'oppositeLineId': '115967692099289456'
        }
    ]

    plan = PlanService.create_plan_nn(subId=subId, isYaoKong=isYaoKong,
                                      userNumberWeight=userNumberWeight,
                                      lineLoadRateThreshold=lineLoadRateThreshold,
                                      isBusBarRecover=isBusBarRecover,
                                      busbarNotRepeatLineList=busbarNotRepeatLineList
                                      )
