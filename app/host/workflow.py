from celery import chord, group, chain, shared_task
import time

@shared_task(bind=True, name='TransientInformation')
def transient_information(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'TransientInformation'


@shared_task(bind=True, name='Ghost')
def ghost(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'Ghost'


@shared_task(bind=True, name='GlobalApertureConstruction')
def global_aperture_construction(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'GlobalApertureConstruction'


@shared_task(bind=True, name='GlobalAperturePhotometry')
def global_aperture_photometry(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'GlobalAperturePhotometry'


@shared_task(bind=True, name='GlobalHostSEDFitting')
def global_host_sed_fitting(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'GlobalHostSEDFitting'


@shared_task(bind=True, name='HostInformation')
def host_information(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'HostInformation'


@shared_task(bind=True, name='ImageDownload')
def image_download(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'ImageDownload'


@shared_task(bind=True, name='LocalAperturePhotometry')
def local_aperture_photometry(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'LocalAperturePhotometry'


@shared_task(bind=True, name='LocalHostSEDFitting')
def local_host_sed_fitting(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'LocalHostSEDFitting'


@shared_task(bind=True, name='MWEBV_Host')
def mwebv_host(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'MWEBV_Host'


@shared_task(bind=True, name='MWEBV_Transient')
def mwebv_transient(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'MWEBV_Transient'


@shared_task(bind=True, name='ValidateGlobalPhotometry')
def validate_global_photometry(self, transient_name):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    if transient_name:
        return transient_name
    else:
        return 'ValidateGlobalPhotometry'


@shared_task(bind=True, name='ValidateLocalPhotometry')
def validate_local_photometry(self, transient_name, sleep=10):
    print(f'''Task "{transient_name}" ({self.request.id}) executing at time: {time.time()}''')
    time.sleep(sleep)
    if transient_name:
        return transient_name
    else:
        return 'ValidateLocalPhotometry'


@shared_task(bind=True, name='TransientWorkflow')
def transient_workflow(self, transient_name=None):
    host_information_sig = host_information.si(transient_name)
    image_download_sig = image_download.si(transient_name)
    mwebv_transient_sig = mwebv_transient.si(transient_name)

    # chord_local_host_sed_fitting = chord(
    #     mwebv_transient_sig,
    #     validate_local_photometry.si(transient_name),
    # )(local_host_sed_fitting.si(transient_name))

    # chain_local_host_sed_fitting = chain(
    #     host_information_sig,
    #     local_aperture_photometry.si(transient_name),
    #     validate_local_photometry.si(transient_name),
    #     chord_local_host_sed_fitting,
    # )
    # chain_global_aperture_photometry = chain(
    #     global_aperture_construction.si(transient_name),
    #     global_aperture_photometry.si(transient_name),
    #     validate_global_photometry.si(transient_name),
    # )
    # header_host_sed_inference = group(
    #     chain_global_aperture_photometry,
    #     mwebv_host.si(transient_name),
    #     host_information_sig,
    #     chain_local_host_sed_fitting,
    # ),
    # chord_host_sed_inference = chord(
    #     header_host_sed_inference,
    # )(global_host_sed_fitting.si(transient_name))

    # workflow = group(
    #     mwebv_transient_sig,
    #     chain(
    #         image_download_sig,
    #         ghost.si(transient_name),
    #         group(
    #             chord_host_sed_inference,
    #             chain_local_host_sed_fitting,
    #         )
    #     )
    # )

    # Execute the workflow
    workflow = chord(
        [
            mwebv_transient.si(transient_name),
            validate_local_photometry.si(transient_name),
        ]
    )(local_host_sed_fitting.si(transient_name))

    return transient_name
