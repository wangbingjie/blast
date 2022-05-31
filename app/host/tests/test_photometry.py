from django.test import TestCase
from ..processing import ApertureConstructionRunner

# python manage.py test host.tests.test_photometry



class PhotometryTest(TestCase):

    fixtures = [
        "setup_test_transient.yaml",
        "setup_tasks.yaml",
        "setup_status.yaml",
        "setup_test_task_register.yaml",
        "setup_test_host.yaml",
        "setup_survey_data.yaml",
        "setup_filter_data.yaml",
        "setup_test_cutout.yaml"
    ]

    def setUp(self):
        self.aperture_runner = ApertureConstructionRunner()

    def test_aperture_construction_runner(self):
        self.aperture_runner.run_process()


    """
    def test_segmentation(self,debug=False):



        transient = Transient.objects.get(name__exact="2010H")
        task = Task.objects.get(name__exact="Aperture construction")
        task_register = TaskRegister.objects.get(transient=transient, task=task)
        host = Host.objects.get(transient=transient)
        cutout = Cutout.objects.filter(filter__name="PanSTARRS_g").get(transient=transient)

        # estimate the background
        #estimate_background(image)

        # get the source catalog
        #build_source_catalog()

        # get the source
        #match_source()

        # get the ellipse params
        #elliptical_sky_aperture()
        image_hdu = fits.open(cutout.fits.__str__())
        aperture = host_utils.construct_aperture(image_hdu, host.sky_coord)

        # plot it up
        # for debugging
        if debug:
            ax = plt.axes()
            wcsim = WCS(image_hdu[0].header)
            xpos,ypos = wcsim.wcs_world2pix(aperture.positions.ra.deg,aperture.positions.dec.deg,0)
            scaled_image = scale_image(image_hdu[0].data)
            ax.imshow(scaled_image,cmap='gray')
            ell = Ellipse(xy=[xpos,ypos],
                          width=2*4*aperture.a.value,
                          height = 2*4*aperture.b.value,
                          angle = (aperture.theta.value*180/3.14+90),
                          lw = 2, fill=False, color = '#fc4e2a')
            ax.add_artist(ell)
            plt.savefig('tmp.png')


        self.assertTrue(np.isclose(aperture.a.value,38.33,0.01))
        self.assertTrue(np.isclose(aperture.b.value,18.81,0.01))
        self.assertTrue(np.isclose(aperture.theta.value,-2.307,0.001))
     """
