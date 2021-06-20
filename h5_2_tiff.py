# coding:utf-8
import numpy as np
import sys
import gdal,gdalconst,osr

__author__ = "TTY6335 https://github.com/TTY6335"

if __name__ == '__main__':

#入力するファイルの情報#
	#ファイル名
	input_file=sys.argv[1]
	#バンド名
	band_name=sys.argv[2]

#出力ファイル名
	output_file=sys.argv[3]

	try:
		hdf_file = gdal.Open(input_file, gdal.GA_ReadOnly)
	except:
		print('%s IS MISSING.' % input_file)
		exit(1);
	
	dataset_list=hdf_file.GetSubDatasets()

	print('OPEN %s.' % input_file)
	# Open HDF file

	# Open raster layer
	#プロダクト名を探す
	product_name='//Image_data/'+band_name
	for dataset_index in range(len(dataset_list)):
#		if('//Geometry_data/Latitude' in dataset_list[dataset_index][0]):
#			lat_index=dataset_index
#		if('//Geometry_data/Longitude' in dataset_list[dataset_index][0]):
#			lon_index=dataset_index
		if(product_name in dataset_list[dataset_index][0]):
			break;

	if not (product_name in dataset_list[dataset_index][0]):
		print('%s IS MISSING.' % band_name)
		print('SELECT FROM')
		for dataset in dataset_list:
			if('Image_data' in dataset[0]):
				print(dataset[0].split('/')[-1])
		exit(1);


	DN=gdal.Open(hdf_file.GetSubDatasets()[dataset_index][0], gdal.GA_ReadOnly).ReadAsArray()

	#Get Sole, Offset,Minimum_valid_DN, Maximum_valid_DN
	Metadata=hdf_file.GetMetadata_Dict()
	hdf_filename=Metadata['Global_attributes_Product_file_name']

	Slope=None
	Offset=None
	Minimum_valid_DN=None
	Maximum_valid_DN=None
	Data_description=None
	for metadata_lavel in Metadata.keys():
		if band_name+'_Slope' in metadata_lavel:
			Slope=float(Metadata[metadata_lavel])
		if band_name+'_Offset' in metadata_lavel:
			Offset=float(Metadata[metadata_lavel])
		if band_name+'_Minimum_valid_DN' in metadata_lavel:
			Minimum_valid_DN=float(Metadata[metadata_lavel])
		if band_name+'_Maximum_valid_DN' in metadata_lavel:
			Maximum_valid_DN=float(Metadata[metadata_lavel])
		if band_name+'_Data_description' in metadata_lavel:
			Data_description=Metadata[metadata_lavel]
	#型変換とエラー値をnanに変換する
	DN=np.array(DN,dtype='uint16')
	if((Maximum_valid_DN is not None) and (Minimum_valid_DN is not None)):
		DN=np.where(DN>=Maximum_valid_DN,np.nan,DN)
		DN=np.where(DN<=Minimum_valid_DN,np.nan,DN)

	#値を求める
	if((Slope is not None) and (Offset is not None)):
		Value_arr=Slope*1275*DN+Offset
#	Value_arr=np.array(Value_arr,dtype='float32')
	Value_arr=np.array(Value_arr,dtype='byte')

	#列数
	lin_size=DN.shape[1]
	#行数
	col_size=DN.shape[0]

	#出力
	dtype = gdal.GDT_Byte
	band=1
	output = gdal.GetDriverByName('GTiff').Create(output_file,lin_size,col_size,band,dtype)
	output.SetGeoTransform((-180,0.041666668, 0,90, 0,-0.041666668))
	output.GetRasterBand(1).WriteArray(Value_arr)
	#projection
	srs = osr.SpatialReference()
	srs.ImportFromEPSG(4326)
	output.SetProjection(srs.ExportToWkt())

	#Add Description
	output.SetMetadata({'Data_description':str(Data_description)})
	output.FlushCache()
	output = None 	
	print('CREATE '+output_file)

#CLOSE HDF FILE
	Image_var=None	
	hdf_file=None
