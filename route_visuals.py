import numpy as np
import folium
import openrouteservice as ors
from numpy.core.numeric import binary_repr
import pandas as pd
from pulp import *
from routeFunctions import *
from routeFuncsNikhil import *
from LP_Formulation import *
from groupingFunctions import *

def find_coords(routes, locations):
    ''' Returns coords of input store matrix.
        Inputs:
        ------
        routes : 2D list
                    2D list containing routes.     

        locations : pandas data frame
                    pandas data frame containing location data of stores  
        Returns:
        --------
        routes : 2D list
                    2D list containing coords of routes (Long, Lat).
    '''
    for i in range(0, len(routes)):
        route = routes[i]
        for j in range(0, len(route)):
            route[j] = locations[locations['Store'].str.contains(route[j])][['Long','Lat']].to_numpy().tolist()
            ##temp = route[j]
            ##route[j] = temp
        routes[i] = route

    return routes

def visualise_weekday(locations, week_routes, m):
    ''' Creates visualisation of supply routes.
        Inputs:
        ------
        week_routes : 2D list
                    2D list containing routes.     

        locations : pandas data frame
                    pandas data frame containing location data of stores  
        
        m : map object

    '''
    locations = locations.drop(["Type", "Location"], axis = 1)
    week_routes_coords = find_coords(week_routes, locations)
    client = ors.Client(key = ORSkey)

    for i in range(0, len(week_routes_coords)):
        
        route = client.directions(
        coordinates = [item for elem in week_routes_coords[i] for item in elem],
        format = 'geojson',
        validate = False  
        )
        folium.PolyLine(locations = [list(reversed(coord))
                                for coord in 
                                route['features'][0]['geometry']['coordinates']]).add_to(m)

        m.save('weekdayRoutes.html')

def visualise_saturday(locations, sat_routes, m):
    ''' Creates visualisation of supply routes.
        Inputs:
        ------
        week_routes : 2D list
                    2D list containing routes.     

        locations : pandas data frame
                    pandas data frame containing location data of stores  
        
        m : map object

    '''
    locations = locations.drop(["Type", "Location"], axis = 1)
    sat_routes_coords = find_coords(sat_routes, locations)
    client = ors.Client(key = ORSkey)

    for i in range(0, len(sat_routes_coords)):
        
        route = client.directions(
        coordinates = [item for elem in sat_routes_coords[i] for item in elem],
        format = 'geojson',
        validate = False  
        )
        folium.PolyLine(locations = [list(reversed(coord))
                                for coord in 
                                route['features'][0]['geometry']['coordinates']]).add_to(m)

        m.save('saturdayRoutes.html')

if __name__ == "__main__":

    ORSkey = '5b3ce3597851110001cf6248d7b8cfb9dc674da68ceee4b1c3212e26'

    locations = pd.read_csv('WoolworthsLocations.csv')

    coords = locations[['Long','Lat']]
    coords = coords.to_numpy().tolist()

    m = folium.Map(location = list(reversed(coords[2])), zoom_start = 10.25)

    for i in range (1, len(coords)):
        if locations.Type[i] == 'Countdown':
            iconCol = 'green'
        elif locations.Type[i] == 'FreshChoice':
            iconcol = 'blue'
        elif locations.Type[i] == 'SuperValue':
            iconCol = 'red'
        elif locations.Type[i] == 'Countdown Metro':
            iconCol = 'orange'
        elif locations.Type[i] == 'Distribution Centre':
            iconCol = 'black'
        folium.Marker(list(reversed(coords[i])), popup = locations.Store[i], icon = folium.Icon(color = iconCol)).add_to(m)


    #hardcoded as I could not find a way to read from LP file
    week_routes = [['Distribution Centre Auckland', 'Countdown Lynfield', 'Countdown Blockhouse Bay'],
    ['Distribution Centre Auckland', 'FreshChoice Mangere Bridge', 'Countdown Three Kings', 'Countdown Onehunga'],
    ['Distribution Centre Auckland', 'Countdown Lynmall', 'Countdown Kelston'],
    ['Distribution Centre Auckland', 'Countdown Mangere Mall', 'Countdown Airport'],
    ['Distribution Centre Auckland', 'Countdown Meadowlands', 'Countdown Botany Downs'],
    ['Distribution Centre Auckland', 'Countdown Manurewa', 'Countdown Mangere East'],
    ['Distribution Centre Auckland', 'Countdown Takanini', 'Countdown Roselands'],
    ['Distribution Centre Auckland', 'SuperValue Papakura', 'Countdown Papakura'],
    ['Distribution Centre Auckland', 'SuperValue Flatbush', 'Countdown Manukau Mall', 'Countdown Manukau'],
    ['Distribution Centre Auckland', 'Countdown Pt Chevalier', 'Countdown Mt Eden'],
    ['Distribution Centre Auckland', 'FreshChoice Otahuhu', 'Countdown Sylvia Park', 'Countdown Papatoetoe'],
    ['Distribution Centre Auckland', 'Countdown St Lukes', 'Countdown Mt Roskill'],
    ['Distribution Centre Auckland', 'Countdown Northwest', 'Countdown Hobsonville'],
    ['Distribution Centre Auckland', 'Countdown Westgate', 'Countdown Lincoln Road'],
    ['Distribution Centre Auckland', 'Countdown Te Atatu South', 'Countdown Te Atatu'],
    ['Distribution Centre Auckland', 'SuperValue Titirangi', 'SuperValue Palomino', 'FreshChoice Ranui'],
    ['Distribution Centre Auckland', 'SuperValue Avondale', 'FreshChoice Glen Eden', 'Countdown Henderson'],
    ['Distribution Centre Auckland', 'Countdown Highland Park', 'Countdown Aviemore Drive'],
    ['Distribution Centre Auckland', 'Countdown St Johns', 'Countdown Meadowbank'],
    ['Distribution Centre Auckland', 'Countdown Pakuranga', 'Countdown Mt Wellington'],
    ['Distribution Centre Auckland', 'FreshChoice Half Moon Bay', 'Countdown Howick'],
    ['Distribution Centre Auckland', 'Countdown Newmarket', 'Countdown Greenlane'],
    ['Distribution Centre Auckland', 'Countdown Ponsonby', 'Countdown Grey Lynn Central'],
    ['Distribution Centre Auckland', 'Countdown Victoria Street West', 'Countdown Auckland City'],
    ['Distribution Centre Auckland', 'Countdown Glenfield', 'Countdown Birkenhead'],
    ['Distribution Centre Auckland', 'Countdown Sunnynook', 'Countdown Grey Lynn'],
    ['Distribution Centre Auckland', 'Countdown Northcote', 'Countdown Hauraki Corner'],
    ['Distribution Centre Auckland', 'Countdown Takapuna', 'Countdown Milford'],
    ['Distribution Centre Auckland', 'Countdown Metro Halsey Street', 'Countdown Browns Bay'],
    ['Distribution Centre Auckland', 'Countdown Metro Albert Street', 'Countdown Mairangi Bay']]
    sat_routes = [['Distribution Centre Auckland', 'Countdown Onehunga', 'Countdown Lynmall', 'Countdown Kelston', 'Countdown Blockhouse Bay'],
    ['Distribution Centre Auckland', 'Countdown Papatoetoe', 'Countdown Manukau Mall', 'Countdown Manukau', 'Countdown Mangere Mall', 'Countdown Airport'],
    ['Distribution Centre Auckland', 'Countdown Takanini', 'Countdown Roselands', 'Countdown Papakura', 'Countdown Manurewa', 'Countdown Mangere East'],
    ['Distribution Centre Auckland', 'Countdown Westgate', 'Countdown Northwest', 'Countdown Hobsonville'],
    ['Distribution Centre Auckland', 'Countdown Te Atatu South', 'Countdown Te Atatu', 'Countdown Lincoln Road', 'Countdown Henderson'],
    ['Distribution Centre Auckland', 'Countdown Sylvia Park', 'Countdown Mt Wellington', 'Countdown Meadowbank', 'Countdown Highland Park', 'Countdown Aviemore Drive'],
    ['Distribution Centre Auckland', 'Countdown St Johns', 'Countdown Pakuranga', 'Countdown Meadowlands', 'Countdown Howick', 'Countdown Botany Downs'],
    ['Distribution Centre Auckland', 'Countdown Three Kings', 'Countdown St Lukes', 'Countdown Mt Roskill', 'Countdown Lynfield'],
    ['Distribution Centre Auckland', 'Countdown Pt Chevalier', 'Countdown Ponsonby', 'Countdown Newmarket', 'Countdown Mt Eden', 'Countdown Greenlane'],
    ['Distribution Centre Auckland', 'Countdown Northcote', 'Countdown Glenfield', 'Countdown Birkenhead', 'Countdown Auckland City'],
    ['Distribution Centre Auckland', 'Countdown Sunnynook', 'Countdown Milford', 'Countdown Mairangi Bay', 'Countdown Browns Bay'],
    ['Distribution Centre Auckland', 'Countdown Victoria Street West', 'Countdown Takapuna', 'Countdown Hauraki Corner', 'Countdown Grey Lynn Central', 'Countdown Grey Lynn']]
    
    visualise_saturday(locations, sat_routes, m)
    visualise_weekday(locations, week_routes, m)
    
    






