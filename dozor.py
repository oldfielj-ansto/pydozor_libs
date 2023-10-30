import numpy as np
from cffi import FFI

ffi = FFI()
ffi.cdef("""
    struct DETECTOR
    {
        int ix, iy;
        int ix_unbinned, iy_unbinned;
        int binning_factor;     
        float pixel;
    };
    
    struct DATACOL
    {
        float wave;
        float dist;
        float monoch;
        float aconst;
        int Ispot;
        float texposure;
        int mrd;
        float hmax2;
        float hmin2;
        float delh2;
        float mgain;
        float backpol[51];
        float backpolP[51];
        float backerr[51];
            
        float IMstep;

        float xcen, ycen;
        float start_angl, phiwidth;
        int number_images,image_first;
        int graph, sprint, backg, rd, isum;
        int w, wg;
        int pr;
        int prAll;
        float vbin[50];
        int pixel_min, pixel_max;
        int Kxmin, Kxmax, Kymin, Kymax;
        int nbad;
        int Bxmin[50], Bxmax[50], Bymin[50], Bymax[50];
        int wedge;
        int pLim1[1101], pLim2[1101];
        float idealback0[50];
        float idealback[150]; //50*3
            
        float RList[51051]; //51*1001
        float hklKoor[102000]; //51*1000*2
        float Ilimit[51];
        
        float vbins[51];
        float vbina[51];
        float Wil[2103]; //3*701

        float beamstop_size;
        float beamstop_distance;
        int beamstop_vertical;
            
        float sigLev;
    };
    
    struct LOCAL
    {
        float cos2tet2[51];
        float pol[765]; //51*15
        float absorb[51];
    };
    
    struct DATACOL_PICKLE
    {
        float backpol2D[51];
        float Rfexp;
        float Iav;
        int NofR;
        float dlim;
        double SumTotal2D, SumBack2D;
        float Coef;
        int table_suc;
        double table_sc;
        double table_b;
        float table_resol;
        float table_corr;
        float table_rfact;
        float table_intsum;
    
        float table_est;      
        float score2;
        float score3;
        float dlim09;
        int   NofS;
    };
    
    struct Reflection
    {
        float x;
        float y;
        float intensity;
    };
    
    void dozor_set_defaults_(struct DATACOL*);
    void read_dozor_(struct DETECTOR*, struct DATACOL*, char[1024], char[1024], char*);
    void pre_dozor_(struct DETECTOR*, struct DATACOL*, struct LOCAL*, char*, char*, int*);
    void dozor_do_image_(short*, struct DETECTOR*, struct DATACOL*, struct DATACOL*, struct DATACOL_PICKLE*, struct LOCAL*, char*, char*);
    void dozor_get_spot_list_(struct DETECTOR*, struct DATACOL*, struct DATACOL_PICKLE*, short*, struct Reflection*);
    """)

dozor = ffi.dlopen('libdozor.so')

class Dozor():
    def __init__(self, config_file):
        self.data_input = ffi.new('struct DATACOL*')
        dozor.dozor_set_defaults_(self.data_input)

        self.detector = ffi.new('struct DETECTOR*')

        self.detector.binning_factor = 1
        
        self.detector.ix = 0
        self.detector.iy = 0
        self.detector.pixel =0.0  #0.075
        fname = ffi.new('char[1024]', config_file)
        templ = ffi.new('char[1024]')
        library = ffi.cast('char*', ffi.NULL) #ffi.new("char**", ffi.NULL)
        dozor.read_dozor_(self.detector, self.data_input, fname, templ, library)

        self.local = ffi.new('struct LOCAL*')
        detector_xy = self.detector.ix * self.detector.iy
        self.PSIim = ffi.new('char[%d]' % detector_xy)
        self.KLim = ffi.new('char[%d]' % detector_xy)
        debug = ffi.new('int*', 0)
        dozor.pre_dozor_(self.detector, self.data_input, self.local, self.PSIim, self.KLim, debug)

    def do_image(self, img):
        data = ffi.new('struct DATACOL_PICKLE*')
        datacol = ffi.new('struct DATACOL*')
        dozor.dozor_do_image_(ffi.cast('short*', ffi.from_buffer(img)), self.detector, 
                              self.data_input, datacol, data, self.local, self.PSIim, self.KLim)
        #print ("get spots results")
        # get spot list
        spots = None
        spots = ffi.new('struct Reflection[%d]' %data.NofR)
        dozor.dozor_get_spot_list_(self.detector, datacol, data, ffi.cast('short*', ffi.from_buffer(img)), spots)
        return data, spots
