#%%
import gdal
from gdalconst import *
from libtiff import TIFF
import numpy as np 


#%%
def readImage(img_path):
    data = []
    # 以只读方式打开遥感影像
    dataset = gdal.Open(img_path, GA_ReadOnly)
    if dataset is None:
        print("Unable to open image file.")
        return data
    else:
        print("Open image file success.")
        geoTransform = dataset.GetGeoTransform()
        print('geoTransform:\n', geoTransform)
        im_proj = dataset.GetProjection()  # 获取投影信息
        print('im_proj:\n', im_proj)
        bands_num = dataset.RasterCount
        print("Image height:" + dataset.RasterYSize.__str__() + " Image width:" + dataset.RasterXSize.__str__())
        print(bands_num.__str__() + " bands in total.")
        for i in range(bands_num):
            # 读取像素值分两步
            # 获取影像的第i+1个波段
            band_i = dataset.GetRasterBand(i + 1)
            # 读取第i+1个波段数据
            band_data = band_i.ReadAsArray(0, 0, band_i.XSize, band_i.YSize)
            data.append(band_data)
            print("band " + (i + 1).__str__() + " read success.")
        
        return geoTransform, im_proj


def writeImage(bands, path, geotrans=None, proj=None):
    projection = [
        # WGS84坐标系(EPSG:4326)
        """GEOGCS["WGS 84", DATUM["WGS_1984", SPHEROID["WGS 84", 6378137, 298.257223563, AUTHORITY["EPSG", "7030"]], AUTHORITY["EPSG", "6326"]], PRIMEM["Greenwich", 0, AUTHORITY["EPSG", "8901"]], UNIT["degree", 0.01745329251994328, AUTHORITY["EPSG", "9122"]], AUTHORITY["EPSG", "4326"]]""",
        # Pseudo-Mercator、球形墨卡托或Web墨卡托(EPSG:3857)
        """PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"],AUTHORITY["EPSG","3857"]]"""
    ]

    if bands is None or bands.__len__() == 0:
        return
    else:
        # 认为各波段大小相等，所以以第一波段信息作为保存
        band1 = bands[0]
        # 设置影像保存大小、波段数
        img_width = band1.shape[1]
        img_height = band1.shape[0]
        num_bands = bands.__len__()

        # 设置保存影像的数据类型
        if 'int8' in band1.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in band1.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32

        # 创建文件
        # 先创建驱动，再创建相应的栅格数据集
        driver = gdal.GetDriverByName("GTiff")
        dataset = driver.Create(path, img_width, img_height, num_bands, datatype)
        if dataset is not None:
            if geotrans is not None:
                dataset.SetGeoTransform(geotrans)  # 写入仿射变换参数
            if proj is not None:
                if proj is 'WGS84' or proj is 'wgs84' or proj is 'EPSG:4326' or proj is 'EPSG-4326' or proj is '4326':
                    dataset.SetProjection(projection[0])  # 写入投影
                elif proj is 'EPSG:3857' or proj is 'EPSG-3857' or proj is '3857':
                    dataset.SetProjection(projection[1])  # 写入投影
                else:
                    dataset.SetProjection(proj)  # 写入投影
            for i in range(num_bands):
                dataset.GetRasterBand(i + 1).WriteArray(bands[i])
        print("save image success.")


#%%
geotrans, proj = readImage('D:\\Data\\MOD09GQ\\h27v05_AllWDays_percent.tiff')

tif = TIFF.open('D:\\Data\\MOD09GQ\\output\\h27v05_before_NIR.tiff', mode='r')
NIR = tif.read_image()
tif = TIFF.open('D:\\Data\\MOD09GQ\\output\\h27v05_before_R.tiff', mode='r')
R = tif.read_image()

geotrans /= np.array([1, 2, 1, 1, 1, 2])
writeImage(np.stack((R, NIR)), 'D:\\Data\\MOD09GQ\\output\\h27v05_before.tiff', \
    geotrans=geotrans, proj=proj)