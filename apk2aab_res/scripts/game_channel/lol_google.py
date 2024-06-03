# #-*- coding:utf-8 -*-
import os
import shutil

from common_util.file_utils import FileUtils
from common_util.invoker import Apk2AabExtraHandler
from constant.param import Apk2AabParam
from constant.path import WorkSpace


class LolGoogleSpecialHandler(Apk2AabExtraHandler):

    def before_merge_params(self):
        return True


    def before_depackage(self):
        return True
        

    def before_compile_res(self):
        # 编译base资源前的处理
        # 修改反编译后生成的$开头的文件名，并在public.xml中同步修改的文件名
        res_dir = os.path.join(WorkSpace.TEMP_APK_ORIGINAL, "res")

        drawable_dir = os.path.join(res_dir, "drawable")
        drawable_v24_dir = os.path.join(res_dir, "drawable-anydpi-v24")
        values_dir = os.path.join(res_dir, "values")
        # 替换文件名
        FileUtils.replaceFileNames(drawable_dir)
        FileUtils.replaceFileNames(drawable_v24_dir)
        
        # 修改报错文件名的内容
        avd_show_password_file = os.path.join(drawable_dir, "avd_show_password.xml")
        avd_hide_password_file = os.path.join(drawable_dir, "avd_hide_password.xml")
        ld_svg_coin_file = os.path.join(drawable_v24_dir, "ld_svg_coin.xml")
        # 修改public.xml中的文件名
        public_file = os.path.join(values_dir, "public.xml")

        FileUtils.replaceFielContent(avd_show_password_file, {"@drawable/$":"@drawable/"})
        FileUtils.replaceFielContent(avd_hide_password_file, {"@drawable/$": "@drawable/"})
        FileUtils.replaceFielContent(ld_svg_coin_file, {"@drawable/$": "@drawable/"})
        FileUtils.replaceFielContent(public_file, {"name=\"$": "name=\""})
        
        return True
    

    def before_link_res(self):
        return True 
    

    def before_arrange_base(self):
        return True  
    

    def before_arrange_assets(self):
        # 在此处配置需要分割的特殊文件
        self.param_dic[Apk2AabParam.ASSESTS_SPACIAL_FILES] = [".ogg"]
        return True  
        
 
    def before_link_assets(self):
        return True


    def before_bundle_build(self):
        return True  


    def before_signer_aab(self):
        return True  


if __name__ == '__main__':
    res_dir = os.path.join(r"E:\apk2aab_tool\tmp\tmp_20240529_154443\apk_original", "res")




