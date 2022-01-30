import os
import csv
import re
import time
import urllib.request
import datetime as dt
import shutil # save img locally
import unicodedata
python_dir = r'C:\Users\money\Downloads\python'
os.chdir(python_dir)
photos_dir = r'C:\Users\money\Downloads\python\photos' + '\\'

status_photos_dir = {'active': photos_dir + 'active' + '\\',
    'draft': photos_dir + 'draft' + '\\',
    'archived': photos_dir + 'archived' + '\\'}

photos_url_file = 'photos_url.csv'
url_csv = False
photos_csv_location = photos_dir + photos_url_file

def download_image(url, file_path, file_name):
    full_path = file_path + file_name
    urllib.request.urlretrieve(url, full_path)  
    

# https://docs.python.org/3/library/unicodedata.html
def convert_to_ascii(string_par):
    string_par = re.sub('×', 'x', string_par)
    string_par = unicodedata.normalize('NFKD', string_par).encode('ascii', 'ignore').decode()
    return string_par

def unix_string(string_par):
    par = string_par.lower()
    par = re.sub('[^a-z0-9_. -]', '', par)
    par = re.sub(' ', '_', par)
    return par

def pad_int(int_par, num_digits):
    int_par = str(int_par)
    while num_digits - len(int_par) > 0:
        int_par = '0' + int_par
    return int_par

option_name_col = ['option1_name',
    'option2_name',
    'option3_name']
option_value_col = ['option1_value',
    'option2_value',
    'option3_value']
def option_string(row_par):
    opt_str = ""
    for x in range(0,3):
        name = option_name_col[x]
        value = option_value_col[x]
        r_value = row[value]
        r_name = row[name]
        if r_value != '' and r_name != '':
            next_option = "{0}-{1}".format(r_name, r_value)
            if opt_str != "":
                opt_str = opt_str + "." + next_option
            else:
                opt_str = next_option
    return opt_str

def image_file_name(image_row_data):
    x = image_row_data
    t = {'main':'a',
        'variant':'b'}
    opt = ""
    if unix_string(x['options']) != '':
        opt = "." + unix_string(x['options'])
    to_p = "{0}-{1}.{2}{3}{4}.jpg".format(unix_string(x['vendor']),unix_string(x['title']),pad_int(x['sub_index'], 2),t[x['main_or_variant']],opt)
    return to_p



files = []
stats = []
for r, d, f in os.walk(python_dir):
    file_type = r"\..*$"
    for file in f:
        f_stats = os.stat(os.path.join(r, file))
        file_loc = r + '\\' + file
        file_d = {'loc':file_loc,
            'mode':f_stats[0],
            'ino':f_stats[1],
            'dev':f_stats[2],
            'nlink':f_stats[3],
            'uid':f_stats[4],
            'gid':f_stats[5],
            'size':f_stats[6],
            'atime':dt.datetime.fromtimestamp(f_stats[7]).strftime('%Y-%m-%d %H:%M.%S'),
            'mtime':dt.datetime.fromtimestamp(f_stats[8]).strftime('%Y-%m-%d %H:%M.%S'),
            'ctime':dt.datetime.fromtimestamp(f_stats[9]).strftime('%Y-%m-%d %H:%M.%S'),
            'f_type':re.findall(file_type,file_loc)[0]}
        
        url_csv = 'photos_url.csv' not in file_d['loc']
        if file_d['f_type'] in ['.csv'] and 'photos_url.csv' not in file_d['loc']:
            stats.append(file_d)
            files.append(file_d)

latest_file = {'file':None,
    'mtime':dt.datetime.fromtimestamp(0).strftime('%Y-%m-%d %H:%M.%S')}
for file in stats:
    if file['mtime'] > latest_file['mtime'] and file['f_type'] == '.csv':
        latest_file = {'file':file['loc'],
            'mtime':file['mtime']}

unique_photos_main = []
urls = []

if url_csv:
    photos_csv = open(photos_csv_location, 'r', encoding='UTF8')
    photos_csv_reader = csv.reader(photos_csv)
    photos_csv_header = header = next(photos_csv_reader)
    
    for row in photos_csv_reader:
        r = {}
        for x in range(0,len(photos_csv_header)):
            r[photos_csv_header[x]] = row[x]
            if photos_csv_header[x] == 'image_url':
                urls.append(row[x])
        unique_photos_main.append(r)
    
    photos_csv.close()



products = latest_file['file']
file = open(products, 'r', encoding='UTF8')

csvreader = csv.reader(file)
header = next(csvreader)
head = []
index = 0
for x in header:
    name = re.sub('[^A-Za-z0-9 ]','', x.lower())
    name = re.sub('[ ]+','_', name)
    y = {'col_name':name,
        'col_index':index,
        'raw_name':x}
    head.append(y)
    index = index + 1


rows = []
index = 0
distinct_items = -1
prev_handle = ''
absolute_index = 0
prev_index = 0

for row in csvreader:
    r = row
    r.append(index)
    R = {}
    for col in head:
        value = convert_to_ascii(r[col['col_index']])
        R[col['col_name']] = value
    if R['handle'] != prev_handle:
        prev_handle = R['handle']
        prev_index = absolute_index
        distinct_items = distinct_items + 1
        index = 0
    R['item_index'] = distinct_items
    R['sub_index'] = index
    R['absolute_index'] = absolute_index
    if R['title'] == '':
        R['title'] = rows[prev_index]['title']
    if R['status'] == '':
        R['status'] = rows[prev_index]['status']
    if R['published'] == '':
        R['published'] = rows[prev_index]['published']
    if R['vendor'] == '':
        R['vendor'] = rows[prev_index]['vendor']
    if R['option1_name'] == 'Title':
        R['option1_name'] = ''
    if R['option1_value'] == 'Default Title':
        R['option1_value'] = ''
    rows.append(R)
    absolute_index = absolute_index + 1
    index = index + 1

new_head = head + [{'col_name': 'item_index', 
    'col_index': 48, 
    'raw_name': 'Item Index'},
    {'col_name': 'sub_index', 
    'col_index': 49, 
    'raw_name': 'Sub-Item Index'},
    {'col_name': 'absolute_index', 
    'col_index': 50, 
    'raw_name': 'Absolute Index'}]

cols = [0, 1, 3, 7, 8, 9, 10, 11, 12, 13, 23, 24, 43, 47, 48, 49, 50]

unique_photos = []

for row in rows:
    url1 = None
    url2 = None
    url1_d = None
    url2_d = None
    if row['image_src'] != '':
        url1 = row['image_src']
        url1 = re.sub('\?v=[0-9]+$', '', url1)
    if row['variant_image'] != '':
        url2 = row['variant_image']
        url2 = re.sub('\?v=[0-9]+$', '', url2)
    url1_found = True
    url2_found = True
    option_str = option_string(row)
    if url1 != None and url1 not in urls:
        urls.append(url1)
        url1_found = False
        url1_d = {'handle':row['handle'],
            'title':row['title'],
            'status':row['status'],
            'vendor':row['vendor'],
            'item_index':row['item_index'],
            'sub_index':row['sub_index'],
            'absolute_index':row['absolute_index'],
            'main_or_variant':'main',
            'image_url':url1,
            'options':option_str}
    if url2 != None and url2 not in urls:
        urls.append(url2)
        url2_found = False
        options = []
        url2_d = {'handle':row['handle'],
            'title':row['title'],
            'status':row['status'],
            'vendor':row['vendor'],
            'item_index':row['item_index'],
            'sub_index':row['sub_index'],
            'absolute_index':row['absolute_index'],
            'main_or_variant':'variant',
            'image_url':url2,
            'options':option_str}
    if url1_d != None:
        url1_d['image_name'] = image_file_name(url1_d)
        unique_photos.append(url1_d)
    if url2_d != None:
        url2_d['image_name'] = image_file_name(url2_d)
        unique_photos.append(url2_d)


#Download only the new photos
for photo in unique_photos:
    download_image(photo['image_url'], status_photos_dir[photo["status"]], photo['image_name'])

unique_photos_main = unique_photos_main + unique_photos
# https://www.pythontutorial.net/python-basics/python-write-csv-file/

photos_csv = open(photos_csv_location, 'w', newline = '')
writer = csv.writer(photos_csv)
photos_csv_header = ['handle', 'title', 'status', 'vendor', 'item_index', 'sub_index', 'absolute_index', 'main_or_variant', 'image_url', 'options', 'image_name']
writer = csv.DictWriter(photos_csv, fieldnames=photos_csv_header)
writer.writeheader()
writer.writerows(unique_photos_main)
photos_csv.close()