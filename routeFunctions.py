def GenerateRoutes(distanceData,stores,storage=None):
    #if storage is not none, write it to a storage with given name, 
    #Storage format as [Route1Name; Route1Time; Route1Shop1, Route1Shop2...], [Route2Name...]
    if storage != None:
        f = open(storage+'.txt', 'w')
    RouteNames = []
    RouteTimes = []
    Routes = []
    '''
    for each Route generated   -    Note that this formatting assumes we are generating routes individually
        #                           Will very likely change as we learn implementation

        # OPTION FOR ROUTE NAMES
        #
        # count=1
        # while True:
        #     count+=1
        #     break
        # RouteNames.append("Route"+str(count))

        # ALTERNATIVE FOR ROUTE NAMES
        # name = ""
        # for nodes in nodeset:
        #     if name != ""
        #         name = name + ","  (separator can be changed)
        #     name = name + node


        # FOR WRITING TO FILE
        if storage != None:        
            f.write(name + ';' + str(time) + ';')
            for i in range(len(Stores)-1):
                f.write(str(storeDeliveries[i]) + ',')
            f.write(str(storeDeliveries[-1]) + '\n')
    
    if storage != None:
        f.close()
    '''

def readRoutes(filename):
    RouteNames=[]
    RouteTimes=[]
    Routes=[]
    #Read route data from our storage file
    with open(filename, 'r') as fp:
        for line in fp:
            ln = line.strip()
            if ln != '':
                splitTxt = ln.split(';')
                RouteNames.append(splitTxt[0])
                RouteTimes.append(splitTxt[1])
                Route=[]
                for x in splitTxt[2].split(','):
                    Route.append(int(x))
                Routes.append(Route) 
    
    return RouteNames, RouteTimes, Routes

def test(storage):
    if storage != None:
        f = open(storage+'.txt', 'w')
    Stores=["Store1","Store2","Store3"]
    for i in range(1,3):
        name=str(i)+str(i)
        time=i*15
        storeDeliveries=[0]*3
        for j in range(3):
            storeDeliveries[j]=i*j
        if storage != None:        
            f.write(name + ';' + str(time) + ';')
            for i in range(len(Stores)-1):
                f.write(str(storeDeliveries[i]) + ',')
            f.write(str(storeDeliveries[-1]) + '\n')
    if storage != None:
        f.close()
    pass
    
    
