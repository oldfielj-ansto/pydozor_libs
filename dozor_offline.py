#!/usr/bin/env python
"""
usage: dozor_offline.py [-h] -m MASTER [-M MASK] [-s START] [-e END]
                        [-c CUT_OFF] [-o OUTPUT] [-n NPROC]

analyze Eiger hdf5 data by dozor

optional arguments:
  -h, --help            show this help message and exit
  -m MASTER, --master MASTER
                        EIGER master file
  -M MASK, --mask MASK  EIGER master file
  -s START, --start START
                        start img
  -e END, --end END     end img
  -c CUT_OFF, --cut_off CUT_OFF
                        cut off for hit rate calculation
  -o OUTPUT, --output OUTPUT
                        output directory
  -n NPROC, --nproc NPROC
                        num of procs
"""
import argparse
import numpy as np
import h5py
import sys
import os
import dozor
import multiprocessing
import bitshuffle

def parseArgs():
    """
    parse user input and return arguments
    """
    parser = argparse.ArgumentParser(description = "analyze Eiger hdf5 data by dozor")

    parser.add_argument("-m", "--master", help="EIGER master file", type=str, required=True)
    parser.add_argument("-M", "--mask", help="EIGER master file", type=str, default=None)
    parser.add_argument("-s", "--start", help="start img", type=int, default=1)
    parser.add_argument("-e", "--end", help="end img", type=int, default=-1)
    parser.add_argument("-c", "--cut_off", help="cut off for hit rate calculation", type=int, default=5)
    parser.add_argument("-o", "--output", help="output directory", type=str, default="dozor_res")
    parser.add_argument("-n", "--nproc", help="num of procs", type=int, default=1)
    
    return parser.parse_args()


def worker(work_num, master_file, dozor_dat, mask, start_img, end_img, output_file, cut_off, return_dict):
    d = dozor.Dozor(dozor_dat.encode())
    hit_num = 0
    output_dir = os.path.dirname(output_file)
    if mask is not None:
        idx = np.where(mask>0)

    try:
        output = open(output_file, "w")
        fh = h5py.File(master_file, 'r')
        cont_size = fh['/entry/data/data_000001'].shape[0]
        data = fh['/entry/data/']
        i=0
        start_cont = int((start_img-1)/cont_size)
        end_cont =int((end_img-1)/cont_size)
        d_cont = None
        #print("container range: ", start_cont, end_cont)
        for i in range(start_cont, end_cont+1):
            start_tmp = int(max(0,start_img-i*cont_size-1))
            end_tmp = int(min(end_img-i*cont_size,cont_size))
            #print ("img range: ", start_tmp, end_tmp)
            dset = "data_%06d" % (i+1)
            h5_cont = data[dset]
            h5_cont_name = h5_cont.file.filename
            d_cont = h5py.File(h5_cont_name)
            h5_data = d_cont['/entry/data/data/']

            for j in range(start_tmp,end_tmp):
                img = h5_data[j]
                # convert data to uint16
                if img.dtype == 'uint32':
                    img = img.astype(np.uint16)
                elif img.dtype == 'uint8':
                    img = img.astype(np.uint16)
 
                # apply mask if it's not None
                if mask is not None:
                    img[idx] = 65535
               
                res, spots = d.do_image(img)
                current_img = i*cont_size+j+1
                #save_spots_adx(current_img, spots, output_dir)
                if res.score3 > cut_off:
                    hit_num += 1
                output.write("img %d %d %f %f\n" % (current_img, res.NofR, res.score3, res.dlim09))
            d_cont.close()
    except Exception as ex:
        raise RuntimeError("Error while running worker %d %s" % (work_num, ex))

    finally:
        if d_cont is not None:
            d_cont.close()
        fh.close()
        output.close()
    return_dict[work_num] = hit_num

def save_spots_adx(img_num, spots, output_dir):
    adx_filename = os.path.join(output_dir, "%06d.adx" % img_num)
    output = ""
    #print (adx_filename)
    spot_num = len(spots)
    for i in range(0,spot_num):
        output += "%d %d %f 1 1\n" % (spots[i].x, spots[i].y, spots[i].intensity)
    with open(adx_filename,"w") as adx:
            adx.write(output)


def gen_dozor_dat(master_file, dozor_filename):
    config = {'nx': 4150, #2070, #4150,
              'ny': 4371, #2167, #4371,
              'pixel': 0.075,
              'pixel_min': 0,
              'pixel_max': 65534,
              'fraction_polarization': 0.99,
              'detector_distance': 0,
              'X-ray_wavelength': 1.0,
              'orgx': 0,
              'orgy': 0,
              'spot_size': 2,
              'exposure': 0.01,
              'oscillation_range': 0.10,
              'ix_min': 0, #1015, #2020,
              'ix_max': 0, #1109, #2190,
              'iy_min': 0, #1050, #1765,
              'iy_max': 0} #2167} #4371}

    with h5py.File(master_file) as f:
        config['nx'] = f['/entry/instrument/detector/detectorSpecific/x_pixels_in_detector'][()]
        config['ny'] = f['/entry/instrument/detector/detectorSpecific/y_pixels_in_detector'][()]
        config['pixel_max'] = f['/entry/instrument/detector/detectorSpecific/countrate_correction_count_cutoff'][()]
        config['orgx'] = f['/entry/instrument/detector/beam_center_x'][()] 
        config['orgy'] = f['/entry/instrument/detector/beam_center_y'][()]
        config['detector_distance'] = f['/entry/instrument/detector/detector_distance'][()] * 1000
        config['X-ray_wavelength'] = f['/entry/instrument/beam/incident_wavelength'][()]
        config['exposure'] = f['/entry/instrument/detector/frame_time'][()]
        config['oscillation_range'] = f['/entry/sample/goniometer/omega_range_average'][()] 

    if config['oscillation_range'] < 0.01:
        config['oscillation_range'] = 0.0001

    try:
        output = ""
        for key, value in config.items():
            output += "%s %s\n" % (key, str(value))
        output +="end"
        with open(dozor_filename,"w") as dozor_dat:
            dozor_dat.write(output)
    except Exception as ex:
        raise RuntimeError("Error while writting dozor.dat file")



if __name__ == "__main__":
    args = parseArgs() # get cmd line args
    master_file = args.master
    start_img = args.start
    end_img = args.end
    output_dir = args.output
    cut_off = args.cut_off
    mask_file = args.mask
    dozor_dat = os.path.join(output_dir, "dozor.dat")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    if end_img <0:
        fh = h5py.File(master_file, 'r')
        img_per_trigger = fh['/entry/instrument/detector/detectorSpecific/nimages'][()]
        triggers = fh['/entry/instrument/detector/detectorSpecific/ntrigger'][()]
        end_img = img_per_trigger * triggers
        #print("total images", end_img)
        fh.close()
    #print (end_img)
    total_img = end_img-start_img+1
    nproc = min(args.nproc,total_img)

    mask = None
    if mask_file is not None:
        with h5py.File(mask_file, 'r') as m:
            mask = m['/data'][:]
            #print(type(mask), mask[1090][1012],mask[1012][1090])
    else:
        with h5py.File(master_file, 'r') as fh:
            mask = fh['/entry/instrument/detector/detectorSpecific/pixel_mask'][()]

    gen_dozor_dat(master_file, dozor_dat)


    procs = []
    img_per_proc = int(total_img / nproc)
    if total_img % nproc >0:
        img_per_proc += 1
    start_tmp = start_img

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    
    for i in range(nproc):
        #print ("image range :", start_tmp, min(end_img, start_tmp+img_per_proc))
        output_file = os.path.join(output_dir, "dozor_res_%d.txt" % i)
        p = multiprocessing.Process(target=worker, args=(i, master_file, dozor_dat, mask, start_tmp, min(end_img, start_tmp+img_per_proc-1), output_file, cut_off,return_dict))
        p.start()
        procs.append(p)
        start_tmp = start_tmp+img_per_proc
    for proc in procs:
        proc.join()
    hit_num = 0
    for key, value in return_dict.items():
        hit_num += value
    perc = "%" 
    print ("Found bragg spots in %d out of %d images and the hit rate is %.1f %s" % (hit_num, total_img, hit_num*100.0/total_img, perc))
