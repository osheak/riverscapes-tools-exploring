"""
Augment VBET with the power of riverscapes context
"""
import argparse
import traceback
import sys
import os
from rscommons import RSProject, dotenv, Logger
from vbet.vbet_report import VBETReport

lyrs_in_out = {
    # VBET_ID: INPUT_ID
    'network_intersected': ['network_intersected', 'RSContext'],
    'DEM': ['DEM', 'RSContext'],
    'SLOPE_RASTER': ['SLOPE', 'RSContext'],
    'HILLSHADE': ['HILLSHADE', 'RSContext'],
    'channel_area_polygons': ['channel_area', 'ChannelArea'],
    'PITFILL': ['PITFILL', 'TauDEM'],
    'DINFFLOWDIR_ANG': ['DINFFLOWDIR_ANG', 'TauDEM'],
    'DINFFLOWDIR_SLP': ['DINFFLOWDIR_SLP', 'TauDEM']
}


def main():

    parser = argparse.ArgumentParser(
        description='VBET XML Augmenter',
        # epilog="This is an epilog"
    )
    parser.add_argument('out_project_xml', help='Input XML file', type=str)
    parser.add_argument('in_xmls', help='Comma-separated list of XMLs in decreasing priority', type=str)
    parser.add_argument('--verbose', help='(optional) a little extra logging ', action='store_true', default=False)

    args = dotenv.parse_args_env(parser)

    # Initiate the log file
    log = Logger('XML Augmenter')
    log.setup(verbose=args.verbose)
    log.title(f'XML Augmenter: {args.out_project_xml}')

    try:
        out_prj = RSProject(None, args.out_project_xml)
        out_prj.rs_meta_augment(
            args.in_xmls.split(','),
            lyrs_in_out
        )

        in_xml = args.in_xmls.split(',')[0]
        out_prj.rs_copy_project_extents(in_xml)

        # if watershed in meta, change the project name
        watershed_node = out_prj.XMLBuilder.find('MetaData').find('Meta[@name="Watershed"]')
        if watershed_node is not None:
            name_node = out_prj.XMLBuilder.find('Name')
            name_node.text = f"Valley Bottom for {watershed_node.text}"

        out_prj.XMLBuilder.write()
        report_path = out_prj.XMLBuilder.find('.//HTMLFile[@id="REPORT"]/Path').text
        report = VBETReport(os.path.join(out_prj.project_dir, report_path), out_prj)
        report.write()

    except Exception as err:
        log.error(err)
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
