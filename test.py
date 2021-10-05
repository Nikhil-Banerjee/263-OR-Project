from routeFuncsNikhil import *
from main import *

def hardcode():
    routes = []
    routes.append(['Distribution Centre Auckland', 'Countdown St Lukes', 'Countdown Pt Chevalier', 'Countdown Grey Lynn Central'])
    routes.append(['Distribution Centre Auckland', 'Countdown Mt Eden', 'Countdown Victoria Street West', 'Countdown Metro Halsey Street', 'Countdown Metro Albert Street'])
    routes.append(['Distribution Centre Auckland', 'FreshChoice Mangere Bridge', 'Countdown Mt Roskill'])
    routes.append(['Distribution Centre Auckland', 'Countdown Onehunga', 'Countdown Three Kings'])
    routes.append(['Distribution Centre Auckland', 'Countdown Lynmall', 'SuperValue Avondale'])
    routes.append(['Distribution Centre Auckland', 'FreshChoice Glen Eden', 'Countdown Kelston'])
    routes.append(['Distribution Centre Auckland', 'Countdown Lynfield', 'Countdown Blockhouse Bay', 'SuperValue Titirangi'])
    routes.append(['Distribution Centre Auckland', 'Countdown Birkenhead', 'Countdown Glenfield'])
    routes.append(['Distribution Centre Auckland', 'Countdown Milford', 'Countdown Browns Bay'])
    routes.append(['Distribution Centre Auckland', 'Countdown Sunnynook', 'Countdown Mairangi Bay'])
    routes.append(['Distribution Centre Auckland', 'SuperValue Papakura', 'Countdown Papakura', 'Countdown Roselands'])
    routes.append(['Distribution Centre Auckland', 'Countdown Ponsonby', 'Countdown Grey Lynn'])
    routes.append(['Distribution Centre Auckland', 'Countdown Takanini', 'Countdown Manurewa', 'Countdown Manukau Mall'])
    routes.append(['Distribution Centre Auckland', 'Countdown Airport', 'Countdown Mangere Mall', 'Countdown Mangere East'])
    routes.append(['Distribution Centre Auckland', 'Countdown Manukau', 'SuperValue Flatbush', 'Countdown Papatoetoe'])
    routes.append(['Distribution Centre Auckland', 'FreshChoice Ranui', 'Countdown Lincoln Road'])
    routes.append(['Distribution Centre Auckland', 'Countdown Te Atatu', 'Countdown Hobsonville'])
    routes.append(['Distribution Centre Auckland', 'Countdown Westgate', 'Countdown Northwest'])
    routes.append(['Distribution Centre Auckland', 'SuperValue Palomino', 'Countdown Henderson', 'Countdown Te Atatu South'])
    routes.append(['Distribution Centre Auckland', 'FreshChoice Otahuhu', 'Countdown Mt Wellington', 'Countdown Sylvia Park'])
    routes.append(['Distribution Centre Auckland', 'Countdown Botany Downs', 'Countdown Meadowlands', 'Countdown Howick'])
    routes.append(['Distribution Centre Auckland', 'Countdown Greenlane', 'Countdown Newmarket', 'Countdown Auckland City'])
    routes.append(['Distribution Centre Auckland', 'Countdown Pakuranga', 'Countdown Highland Park', 'Countdown Aviemore Drive'])
    routes.append(['Distribution Centre Auckland', 'FreshChoice Half Moon Bay', 'Countdown St Johns', 'Countdown Meadowbank'])
    # One route was missing but it had to be one of these 6
    routes.append(['Distribution Centre Auckland', 'Countdown Takapuna', 'Countdown Northcote', 'Countdown Hauraki Corner'])
    routes.append(['Distribution Centre Auckland', 'Countdown Takapuna', 'Countdown Hauraki Corner', 'Countdown Northcote'])
    routes.append(['Distribution Centre Auckland', 'Countdown Hauraki Corner', 'Countdown Northcote', 'Countdown Takapuna'])
    routes.append(['Distribution Centre Auckland', 'Countdown Hauraki Corner', 'Countdown Takapuna', 'Countdown Northcote'])
    routes.append(['Distribution Centre Auckland', 'Countdown Northcote', 'Countdown Takapuna', 'Countdown Hauraki Corner'])
    routes.append(['Distribution Centre Auckland', 'Countdown Northcote', 'Countdown Hauraki Corner', 'Countdown Takapuna'])

    return routes

def test(routes,demand):
    longRoutes=[]
    for route in range(len(routes)):
        if (calculateRouteTime(routes[route])/60)+7.5*sum([demand[store] for store in routes[route][1:]]) > 240:
            longRoutes.append(routes[route])
    return longRoutes

if __name__ == "__main__":
    demands = pd.read_csv('WoolworthsDemands.csv', index_col=0)
    wkDayDemand = averageDemand(demands,"Weekday")
    testRoutes = hardcode()
    testvariable = test(testRoutes, wkDayDemand)