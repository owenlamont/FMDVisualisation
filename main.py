from typing import List

import pandas as pd
import geopandas as gpd
from pandas import ExcelFile
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def main():
    excel_data: ExcelFile = ExcelFile("FMDdata.xlsx")
    orig_report_years: List[pd.DataFrame] = []
    report_years: List[pd.DataFrame] = []
    for year in range(7, 17):
        orig_report_years.append(pd.read_excel(excel_data, sheet_name=f'20{year:02}'))

    year = 2007
    for yearly_report in orig_report_years:
        yearly_report = yearly_report.rename(columns={"Country name": "NAME"})
        yearly_report = yearly_report.groupby(["NAME"], as_index=False).sum()
        yearly_report['Year'] = year
        report_years.append(yearly_report)
        year += 1

    world = gpd.read_file("natural_earth_vector/10m_cultural/ne_10m_admin_0_countries.shp")
    world_fmd_report: List[gpd.GeoDataFrame] = []
    for report in report_years:
        report["NAME"].replace(to_replace="China (People's Rep. of)", value="China", inplace=True)
        report["NAME"].replace(to_replace="Congo (Dem. Rep. of the)", value="Dem. Rep. Congo", inplace=True)
        report["NAME"].replace(to_replace="Korea (Dem. People's Rep.)", value="North Korea", inplace=True)
        report["NAME"].replace(to_replace="Palestinian Auton. Territories", value="Palestine", inplace=True)
        report["NAME"].replace(to_replace="Chinese Taipei", value="Taiwan", inplace=True)
        report["NAME"].replace(to_replace="Hong Kong (SAR - PRC)", value="Hong Kong", inplace=True)
        report["NAME"].replace(to_replace="Korea (Rep. of)", value="South Korea", inplace=True)
        map: gpd.GeoDataFrame = world.copy()
        map_disease: gpd.GeoDataFrame = pd.merge(left=map, right=report, how="outer", on="NAME")#pd.concat([map, report], axis=1, sort=False)
        map_disease.fillna(value=0, inplace=True)
        map_disease["AllAnimals"] = map_disease["Cattle"] + \
                                    map_disease["Swine"] + \
                                    map_disease["Sheep"] + \
                                    map_disease["Sheep/goat"] + \
                                    map_disease["Goat"] + \
                                    map_disease["Wild species"] + \
                                    map_disease["Buffalo"] + \
                                    map_disease["Cervidae"] + \
                                    map_disease["Camelidae"] + \
                                    map_disease["Unknown species"]

        world_fmd_report.append(map_disease)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_aspect('equal')

    def init():
        return world_fmd_report[0].plot(ax=ax, column="AllAnimals")

    def update(frame):
        nonlocal world_fmd_report
        nonlocal ax
        return world_fmd_report[frame].plot(ax=ax, column="AllAnimals")

    ani = animation.FuncAnimation(fig, update, init_func=init, frames=9, interval=500, blit=False)
    plt.show()


if __name__ == '__main__':
    main()
