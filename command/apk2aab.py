import os
import shutil
import time
import zipfile

from command.base import BaseCommand, MainlineTask
from common_util.annotation import mainline
from common_util.apk_cmd import ApkCMD
from common_util.bundle_cmd import BundleCMD
from common_util.common import is_not_empty
from common_util.file_utils import FileUtils
from common_util.invoker import Apk2AabSpecialHandler
from common_util.param import get_properties, replace_dic_placeholders
from constant.param import Apk2AabParam, CmdParam, Apk2AabEnvirParam, PackParam
from constant.path import PackEnvirConfig, WorkSpace


class Apk2AabCommand(BaseCommand):
    """
    apk2aab 命令行工具 
    """

    def __init__(self, cmd_args):
        super(Apk2AabCommand, self).__init__(cmd_args)
        self.apk2aab_special_handler = Apk2AabSpecialHandler(self.param_dic)

    def _config_params(self, param_dic):
        return MergeParamTask(self.cmd_args, param_dic, self.apk2aab_special_handler).execute()

    def _config_workspace(self, param_dic):
        return WorkSpaceTask(param_dic, self.apk2aab_special_handler).execute()
        
    def _on_build(self, param_dic):
        apk_path = param_dic[CmdParam.ARGS.SRC]
        output_aab_file = None
        if is_not_empty(CmdParam.ARGS.OUT, param_dic) and param_dic[CmdParam.ARGS.OUT]:
            # 命令行配置的是文件则输出到文件，是目录则生成自定义名称到目录下
            if os.path.isfile(param_dic[CmdParam.ARGS.OUT]):
                output_aab_file = param_dic[CmdParam.ARGS.OUT]
            else:
                output_aab_name = "{0}_{1}_{2}.aab".format(param_dic[PackParam.PACKAGE_NAME], param_dic[PackParam.VERSION_NAME], time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
                output_aab_file = os.path.join(param_dic[CmdParam.ARGS.OUT], output_aab_name)
            return ApkAabTask(apk_path, output_aab_file, param_dic, self.apk2aab_special_handler).execute()
        else:
            return False

    def _on_finish(self, param_dic):
        return True
    
class MergeParamTask(MainlineTask):
    """
    参数合并任务
    """
    def __init__(self, cmd_args, param_dic, apk2aab_special_handler):
        super(MergeParamTask, self).__init__(param_dic)
        self.cmd_args = cmd_args
        self.apk2aab_special_handler = apk2aab_special_handler
        

    @mainline(step=1, desc="读取环境配置文件，默认参数文件，后台参数配置文件，合并到参数集合。")
    def merge_envir_params(self, param_dic):
        param_dic.update(self.cmd_args)
        self.logger.info("apk2aab 工具配置文件：" + PackEnvirConfig.PACKAGE_ENVIR_FILE)
        self.logger.info("apk2aab 默认参数文件：" + PackEnvirConfig.DEFAULT_PARAM_FILE)
        param_dic.update(get_properties(PackEnvirConfig.PACKAGE_ENVIR_FILE))  # package_envir.properties文件参数
        param_dic.update(get_properties(PackEnvirConfig.DEFAULT_PARAM_FILE))  # default_param.properties文件参数
        param_dic.update(get_properties(self.cmd_args[CmdParam.ARGS.CONF]))  # 配置的参数文件，合并到参数集
        replace_dic_placeholders(param_dic, PackParam.GAME_LABEL)  # 使用字典中现有参数填充变量  {game_label}
        replace_dic_placeholders(param_dic, PackParam.SDK_LABEL)  # 使用字典中现有参数填充变量  {sdk_label}
        return True

    @mainline(step=2, desc="读取后台命令行参数和后台配置的参数文件extra_cmd字段，合并到参数集")
    def merge_cmd_params(self, param_dic):
        param_dic.update(self.cmd_args)
        # 根据参数文件的extra_cmd字段，判断参数是否需要修改。 EXTRA_CMD 参数优先级最高
        if param_dic[PackParam.EXTRA_CMD]:  # package_param.properties文件extra_param字段参数优先级5
            self.logger.info("有配置额外参数，%s " % param_dic[PackParam.EXTRA_CMD])
            extra_params = param_dic[PackParam.EXTRA_CMD].split(' ')
            # extra_params.update(param_dic[PackParam.EXTRA_CMD].split(','))
            for extra_param in extra_params:
                # self.logger.info(extra_param)
                if extra_param.startswith("--") and extra_param.find("=") >= 0:  # 如 --target_sdkversion=28
                    key_value = extra_param.split('=')
                    param_dic[key_value[0].strip().lstrip("--")] = key_value[1]
                    self.logger.info("设置 %s 为 %s" % (key_value[0].strip().lstrip("--"), key_value[1]))
                # 如 -d, --keeptmp。不支持多个option一起，如-kd
                if extra_param.startswith("-") and extra_param.find("=") == -1: # 如 -keeptmp 或 --keeptmp
                    key = extra_param
                    key = key.lstrip("-")
                    if key == "keeptmp" or key == "k":
                        param_dic[CmdParam.OPTIONS.KEEP] = True
                    if key == "debug" or key == "d":
                        param_dic[CmdParam.OPTIONS.DEBUG] = True
                    param_dic[key] = True
                    self.logger.info("设置 %s 为 %s" % (key.lstrip("-"), "True"))
        else:
            self.logger.info("没有配置extra_cmd参数。")
        return True
    
    @mainline(step=3, desc="填充所有参数中的变量占位符")
    def fill_all_variable(self, param_dic):
        replace_dic_placeholders(param_dic)
        return True
    
    @mainline(step=4, desc="执行参数相关的特殊逻辑。")
    def param_special_logic(self, param_dic):
        succ = self.apk2aab_special_handler.handle_before_merge_params()
        self.logger.info("最终参数集：" + str(param_dic))
        return succ

class WorkSpaceTask(MainlineTask):
    """
    工作目录相关任务
    """
    def __init__(self, param_dic, apk2aab_special_handler):
        super(WorkSpaceTask, self).__init__(param_dic)
        self.apk2aab_special_handler = apk2aab_special_handler

    @mainline(step=1, desc="创建临时工作目录。")
    def create_tmp_workspace(self, param_dic):
        if is_not_empty(CmdParam.ARGS.WORKSPACE, param_dic):
            WorkSpace.TEMP_FOLDER = os.path.join(param_dic[CmdParam.ARGS.WORKSPACE], "tmp_" + time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())))
            WorkSpace.TEMP_APK_ORIGINAL = os.path.join(WorkSpace.TEMP_FOLDER, "apk_original")
            WorkSpace.TEMP_AAB_PROJECT = os.path.join(WorkSpace.TEMP_FOLDER, "aab_project")
            WorkSpace.TEMP_BASE_MODULE = os.path.join(WorkSpace.TEMP_AAB_PROJECT, "base")
            WorkSpace.TEMP_ASSETS_MODULE = os.path.join(WorkSpace.TEMP_AAB_PROJECT, param_dic[Apk2AabEnvirParam.ASSETS_MODULE_NAME])

            WorkSpace.TEMP_OTHER = os.path.join(WorkSpace.TEMP_FOLDER, "other")

        self.logger.info("创建目录：" + WorkSpace.TEMP_FOLDER)
        os.makedirs(WorkSpace.TEMP_FOLDER)
        self.logger.info("创建目录：" + WorkSpace.TEMP_APK_ORIGINAL)
        os.makedirs(WorkSpace.TEMP_APK_ORIGINAL)
        self.logger.info("创建目录：" + WorkSpace.TEMP_AAB_PROJECT)
        os.makedirs(WorkSpace.TEMP_AAB_PROJECT)
        self.logger.info("创建目录：" + WorkSpace.TEMP_BASE_MODULE)
        os.makedirs(WorkSpace.TEMP_BASE_MODULE)
        self.logger.info("创建目录：" + WorkSpace.TEMP_ASSETS_MODULE)
        os.makedirs(WorkSpace.TEMP_ASSETS_MODULE)
        self.logger.info("创建目录：" + WorkSpace.TEMP_OTHER)
        os.makedirs(WorkSpace.TEMP_OTHER)
        return True

class ApkAabTask(MainlineTask):

    def __init__(self, origin_apk, output_aab, param_dic, apk2aab_special_handler):
        super(ApkAabTask, self).__init__(param_dic)
        self.apk2aab_special_handler = apk2aab_special_handler
        # 原 apk 和输出的 aab
        self.origin_apk = origin_apk
        self.output_aab = output_aab
        # 工具
        self.apktool = param_dic[Apk2AabEnvirParam.APK_TOOL]
        self.smali = param_dic[Apk2AabEnvirParam.SMALI_JAR]
        self.bundle_tool = param_dic[Apk2AabEnvirParam.BUNDLE_TOOL]
        self.aapt = param_dic[Apk2AabEnvirParam.AAPT2]
        self.android_jar = param_dic[Apk2AabEnvirParam.ANDROID_JAR]
        self.jar_signer = param_dic[Apk2AabEnvirParam.APK_SIGNER]
        self.jar_signer = param_dic[Apk2AabEnvirParam.JAR_SIGNER]
        # aab 的目录
        self.base_apk = os.path.join(WorkSpace.TEMP_OTHER, "base.apk")
        self.base_dir = os.path.join(WorkSpace.TEMP_AAB_PROJECT, "base")
        self.base_zip = os.path.join(WorkSpace.TEMP_AAB_PROJECT, "base.zip")

        self.compile_zip = os.path.join(WorkSpace.TEMP_OTHER, "compile.zip")

        self.assets_apk = os.path.join(WorkSpace.TEMP_OTHER, "AssetsPackGameRes.apk")
        self.assets_dir = os.path.join(WorkSpace.TEMP_AAB_PROJECT, "AssetsPackGameRes")
        self.assets_zip = os.path.join(WorkSpace.TEMP_AAB_PROJECT, "AssetsPackGameRes.zip")
        
    @mainline(step=0.5, desc="反编译前的特殊处理")
    def before_depackage(self, param_dic):
        result = self.apk2aab_special_handler.handle_before_depackage()
        return result
        
    @mainline(step=1, desc="反编译APK 文件。")
    def depackage(self, param_dic):
        result = ApkCMD.depackage(self.apktool, self.origin_apk, WorkSpace.TEMP_APK_ORIGINAL, False, True)
        return result
        
    @mainline(step=1.5, desc="编译资源前的特殊处理")
    def before_compile_res(self, param_dic):
        result = self.apk2aab_special_handler.handle_before_compile_res()
        return result
    
    @mainline(step=2, desc="编译资源。")
    def compileRes(self, param_dic):
        res_path = os.path.join(WorkSpace.TEMP_APK_ORIGINAL, "res")
        if not os.path.exists(res_path):
            return False
        result = BundleCMD.compileZip(param_dic[Apk2AabEnvirParam.AAPT2], res_path, self.compile_zip)
        return result
    
    @mainline(step=2.5, desc="链接 base 资源前的特殊处理")
    def before_link_res(self, param_dic):
        result = self.apk2aab_special_handler.handle_before_link_res()
        return result
        
    @mainline(step=3, desc="链接 base 资源。")
    def linkRes(self, param_dic):
        manifest = os.path.join(WorkSpace.TEMP_APK_ORIGINAL, "AndroidManifest.xml")

        result = BundleCMD.linkRes(param_dic[Apk2AabEnvirParam.AAPT2], self.compile_zip, param_dic[Apk2AabEnvirParam.ANDROID_JAR], manifest,
                         param_dic[PackParam.MIN_SDK_VERSION], param_dic[PackParam.TARGET_SDK_VERSION], param_dic[PackParam.COMPILE_VERSION], param_dic[PackParam.VERSION_CODE], param_dic[PackParam.VERSION_NAME], self.base_apk)
        return result

    @mainline(step=3.5, desc="整理 base 模块前的特殊处理")
    def before_arrange_base(self, param_dic):
        result = self.apk2aab_special_handler.handle_before_arrange_base()
        return result 
    
    @mainline(step=4, desc="整理 base 模块。")
    def arrangeBaseApk(self, param_dic):
        # 整理 base 模块
        try:
            move_dict = {}
            with zipfile.ZipFile(self.base_apk, 'a') as zf:
                zf.extractall(self.base_dir)
            manifest_dir = os.path.join(self.base_dir, "manifest")
            # 移动 manifest
            old_manifest = os.path.join(self.base_dir, "AndroidManifest.xml")
            new_manifest = os.path.join(manifest_dir, "AndroidManifest.xml")
            move_dict[old_manifest] = new_manifest
            # 移动 assets
            old_assets = os.path.join(WorkSpace.TEMP_APK_ORIGINAL, "assets")
            new_assets = os.path.join(self.base_dir, "assets")
            move_dict[old_assets] = new_assets
            # 移动 lib
            old_lib = os.path.join(WorkSpace.TEMP_APK_ORIGINAL, "lib")
            new_lib = os.path.join(self.base_dir, "lib")
            move_dict[old_lib] = new_lib

            # 先移动 其他文件夹到 unknown，再统一移动到新的 root 下
            old_unknown_dir = os.path.join(WorkSpace.TEMP_APK_ORIGINAL, "unknown")
            old_kotlin_dir = os.path.join(WorkSpace.TEMP_APK_ORIGINAL, "kotlin")
            old_meta_inf_dir = os.path.join(WorkSpace.TEMP_APK_ORIGINAL, "original/META-INF")
            new_kotlin_dir = os.path.join(old_unknown_dir, "kotlin")
            new_meta_inf_dir = os.path.join(old_unknown_dir, "META-INF")

            move_dict[old_kotlin_dir] = new_kotlin_dir
            move_dict[old_meta_inf_dir] = new_meta_inf_dir

            # 移动 unknown 到新的 root 下
            root_dir = os.path.join(self.base_dir, "root")
            move_dict[old_unknown_dir] = root_dir
            # 移动 dex
            new_dex_dir = os.path.join(self.base_dir, "dex")
            for root, dirs, files in os.walk(WorkSpace.TEMP_APK_ORIGINAL):
                for file in files:
                    file_name = os.path.basename(file)
                    full_path = os.path.join(root, file)
                    if file_name.endswith(".dex"):
                        move_dict[full_path] = os.path.join(new_dex_dir, file)
            result = True
            for old, new in move_dict.items():
                if os.path.exists(old):
                    if os.path.isfile(old):
                        self.logger.info(old+" -> "+new)
                        if not os.path.exists(os.path.dirname(new)):
                            self.logger.info("make dir："+os.path.dirname(new))
                            os.makedirs(os.path.dirname(new))
                        shutil.move(old, new)
                    else:
                        self.logger.info(old+" -> "+new)
                        shutil.copytree(old, new)
                else:
                    self.logger.info(old+" is not exists.")
                    result = False
            return result
        except Exception as e:
            self.logger.info(str(e))
            return False
    
    @mainline(step=4.5, desc="整理 assets 模块前的特殊处理")
    def before_arrange_assets(self, param_dic):
        # 默认的特殊文件，如果有指定可以在script里面再修改
        self.param_dic[Apk2AabParam.ASSESTS_SPACIAL_FILES] = [".bundle", ".mp4", "GameConfig.txt", "bundlemap.map.txt", "progress.json"]
        result = self.apk2aab_special_handler.handle_before_arrange_assets()
        return result 
        
    @mainline(step=5, desc="整理 assets 模块。")
    def arrangeAssets(self, param_dic):
        # 整理 assets 模块
        base_assets = os.path.join(self.base_dir, "assets")
        new_assets = os.path.join(self.assets_dir, "assets")

        # 计算APK文件大小并转换为MB
        size = os.path.getsize(self.origin_apk) / (1024.0 ** 2)
        
        if size > 200+1024:
            # 如果APK文件超过1224MB，则无法分割资源
            self.logger.info("apk 过大，无法分割 assets")
            return False
        elif size > 200:
            try:
                # 如果APK文件大小大于200MB，则开始分割资源
                self.logger.info("apk 小于1224MB，开始分割 assets")
                if not os.path.exists(new_assets):
                    os.makedirs(new_assets)
                for root, dirs, files in os.walk(base_assets):
                    # 如果是文件夹就移到 切割的assets
                    for dir in dirs:
                        full_dir_path = os.path.join(root, dir)
                        new_dir_path = os.path.join(new_assets, dir)
                        self.logger.info("assets 分割："+full_dir_path+"->"+new_dir_path)
                        shutil.move(full_dir_path, new_dir_path)

                    for file in files:
                        old_full_file_path = os.path.join(root, file)
                        new_file_path = os.path.join(new_assets, file)
                        # 移动特定类型的文件至切割的assets
                        for special_file in self.param_dic[Apk2AabParam.ASSESTS_SPACIAL_FILES]:
                            if special_file in os.path.basename(file):
                                self.logger.info("存在此特殊文件:"+special_file+"，移动："+old_full_file_path+"->"+new_file_path)
                                shutil.move(old_full_file_path, new_file_path)
            except Exception as e:
                self.logger.info(str(e))
                return False
        return True

    @mainline(step=5.5, desc="链接 assets 资源前的特殊处理")
    def before_link_assets(self, param_dic):
        result = self.apk2aab_special_handler.handle_before_link_assets()
        return result
        
    @mainline(step=6, desc="链接 assets 资源。")
    def linkAssets(self, param_dic):
        manifest_dir = os.path.join(self.assets_dir, "manifest")
        os.makedirs(manifest_dir)
        manifest = os.path.join(self.assets_dir, "AndroidManifest.xml")
        new_manifest = os.path.join(manifest_dir, "AndroidManifest.xml")
        shutil.copyfile(param_dic[Apk2AabEnvirParam.TEMP_MANIFEST], manifest)
        # 将manifest里面的${package_name}替换成包名
        kvs ={"${applicationId}":param_dic[PackParam.PACKAGE_NAME],\
                "${moduleName}": param_dic[Apk2AabEnvirParam.ASSETS_MODULE_NAME],\
                "${compileSdkVersion}": param_dic[Apk2AabEnvirParam.COMPILE_SDK_VERSION],\
                "${compileSdkVersionCodename}": param_dic[Apk2AabEnvirParam.COMPILE_SDK_VERSION_CODE_NAME],\
                "${platformBuildVersionCode}": param_dic[Apk2AabEnvirParam.PLATFORM_BUILD_VERSION_CODE],\
                "${platformBuildVersionName}": param_dic[Apk2AabEnvirParam.PLATFORM_BUILD_VERSION_NAME]}

        FileUtils.replaceFielContent(manifest, kvs)

        result = BundleCMD.linkResByDir(param_dic[Apk2AabEnvirParam.AAPT2], self.android_jar, manifest, self.assets_apk)

        if result:
                # 如果链接成功，解压并移动manifest文件
            with zipfile.ZipFile(self.assets_apk, 'a') as zf:
                zf.extractall(self.assets_dir)
            shutil.move(manifest, new_manifest)
        return result

    @mainline(step=6.5, desc="构建 AAB 文件前的特殊处理")
    def before_bundle_build(self, param_dic):
        result = self.apk2aab_special_handler.handle_before_bundle_build()
        return result
         
    @mainline(step=7, desc="构建 AAB 文件。")
    def bundleBuild(self, param_dic):
        # 构建 AAB 文件
        zip_txt = ""
        with zipfile.ZipFile(self.base_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for dirpath, dirnames, filenames in os.walk(self.base_dir):
                fpath = dirpath.replace(self.base_dir, '')
                fpath = fpath and fpath + os.sep or ''
                for filename in filenames:
                    zf.write(os.path.join(dirpath, filename), fpath+filename)
        zip_txt += self.base_zip

        with zipfile.ZipFile(self.assets_zip, 'w', zipfile.ZIP_DEFLATED) as zf2:
            for dirpath, dirnames, filenames in os.walk(self.assets_dir):
                fpath = dirpath.replace(self.assets_dir, '')
                fpath = fpath and fpath + os.sep or ''
                for filename in filenames:
                    if filename != "resources.pb":
                        zf2.write(os.path.join(dirpath, filename), fpath+filename)
            zip_txt += (","+self.assets_zip)
        return BundleCMD.buildBundle(self.bundle_tool, zip_txt, self.output_aab)

    @mainline(step=7.5, desc="AAB 文件签名前的特殊处理")
    def before_signer_aab(self, param_dic):
        result = self.apk2aab_special_handler.handle_before_signer_aab()
        return result 
        
    @mainline(step=8, desc="AAB 文件签名。")
    def signerAab(self, param_dic): 
        # 对aab 进行签名
        result = BundleCMD.signBundle(self.jar_signer, self.output_aab, param_dic[PackParam.KEY_STORE_NAME], param_dic[PackParam.KEY_STORE_STOREPASS], param_dic[PackParam.KEY_STORE_KEYPASS], param_dic[PackParam.KEY_STORE_ALIAS])
        return result


