from datetime import datetime
from tool import ToolUtil
from flask import Response
from .setup import *
from .gugutv_handle import Gugutv



class ModuleMain(PluginModuleBase):

    def __init__(self, P):
        super(ModuleMain, self).__init__(P, name='main', first_menu='list')


    def process_menu(self, page_name, req):
        arg = P.ModelSetting.to_dict()
        arg['api_m3u'] = ToolUtil.make_apikey_url(f"/{P.package_name}/api/m3u")
        arg['api_yaml'] = ToolUtil.make_apikey_url(f"/{P.package_name}/api/yaml")
        return render_template(f'{P.package_name}_{self.name}_{page_name}.html', arg=arg)
    
    

    def process_command(self, command, arg1, arg2, arg3, req):
        if command == 'broad_list':
            updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return jsonify({"list": Gugutv.ch_list(), "updated_at": updated_at})
        elif command == 'play_url':
            url = arg3 if arg3 else ToolUtil.make_apikey_url(f"/{P.package_name}/api/url.m3u8?ch_id={arg1}&ch_title={arg2}")
            ret = {'ret':'success', 'data':url, 'title': arg2}
        return jsonify(ret)


    def process_api(self, sub, req):
        try:
            if sub == 'm3u':
                return Gugutv.make_m3u()
            elif sub == 'url.m3u8':
                mode, data = Gugutv.get_m3u8(req.args.get('ch_id'),req.args.get('ch_title'))
                if mode == 'text':
                    return data
                else:
                    return redirect(data)
            elif sub == 'yaml':
                data = Gugutv.make_yaml()
                return Response(data, headers={'Content-Type': 'text/yaml; charset=utf-8'})
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())

