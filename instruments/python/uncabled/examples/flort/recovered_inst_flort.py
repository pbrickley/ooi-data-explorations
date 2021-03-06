#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from instruments.python.common import list_deployments, get_deployment_dates, get_vocabulary, m2m_request, m2m_collect, \
    update_dataset, CONFIG
from instruments.python.uncabled.request_flort import flort_instrument


def main():
    # Setup needed parameters for the request, the user would need to vary these to suit their own needs and
    # sites/instruments of interest. Site, node, sensor, stream and delivery method names can be obtained from the
    # Ocean Observatories Initiative web site. The last two will set path and naming conventions to save the data
    # to the local disk
    site = 'CE01ISSM'           # OOI Net site designator
    node = 'SBD17'              # OOI Net node designator
    sensor = '06-FLORTD000'     # OOI Net sensor designator
    stream = 'flort_sample'     # OOI Net stream name
    method = 'recovered_inst'   # OOI Net data delivery method
    level = 'buoy'              # local directory name, level below site
    instrmt = 'flort'           # local directory name, instrument below level

    # We are after recovered instrument data. Determine list of deployments and use a more recent deployment to
    # determine the start and end dates for our request.
    vocab = get_vocabulary(site, node, sensor)[0]
    deployments = list_deployments(site, node, sensor)
    deploy = deployments[5]
    start, stop = get_deployment_dates(site, node, sensor, deploy)

    # request and download the data
    r = m2m_request(site, node, sensor, method, stream, start, stop)
    flort = m2m_collect(r, '.*FLORT.*\\.nc$')
    flort = flort.where(flort.deployment == deploy, drop=True)  # limit to the deployment of interest

    # clean-up and reorganize
    flort = flort_instrument(flort)
    flort = update_dataset(flort, vocab['maxdepth'])

    # save the data
    out_path = os.path.join(CONFIG['base_dir']['m2m_base'], site.lower(), level, instrmt)
    out_path = os.path.abspath(out_path)
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    out_file = ('%s.%s.%s.deploy%02d.%s.%s.nc' % (site.lower(), level, instrmt, deploy, method, stream))
    nc_out = os.path.join(out_path, out_file)

    flort.to_netcdf(nc_out, mode='w', format='NETCDF4', engine='netcdf4')


if __name__ == '__main__':
    main()