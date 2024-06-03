import os
import shutil
import time

from common_util.common import Logger


class PackEnvirConfig:
    PACKAGE_ENVIR_FILE = os.path.join("apk2aab_res/config", "package_envir.properties")
    DEFAULT_PARAM_FILE = os.path.join("apk2aab_res/config", "default_param.properties")

class WorkSpace:

    # tmp/tmp_20220627_173310
    TEMP_FOLDER = os.path.join("tmp", "tmp_" + time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())))

    # tmp/tmp_20220627_173310/apk_original
    TEMP_APK_ORIGINAL = os.path.join(TEMP_FOLDER, "apk_original")

    TEMP_AAB_PROJECT = os.path.join(TEMP_FOLDER, "aab_project")
    TEMP_BASE_MODULE = os.path.join(TEMP_AAB_PROJECT, "base")
    TEMP_ASSETS_MODULE = os.path.join(TEMP_AAB_PROJECT, "AssetsPackGameRes")

    TEMP_OTHER = os.path.join(TEMP_FOLDER, "other")


class SdkTemplate:
    RES = "res"
    MANIFEST = "AndroidManifest.xml"
    SRC = "src"
    ASSETS = "assets"
    LIBS = "libs"
    LIBS_PREDEX = "libs_predex"



    def __init__(self, root):
        self.root = root

    def __str__(self):
        return self.root

    @property
    def res(self):
        return os.path.join(self.root, SdkTemplate.RES)

    @property
    def libs(self):
        return os.path.join(self.root, SdkTemplate.LIBS)

    @property
    def libs_predex(self):
        return os.path.join(self.root, SdkTemplate.LIBS_PREDEX)

    @property
    def src(self):
        return os.path.join(self.root, SdkTemplate.SRC)

    @property
    def assets(self):
        return os.path.join(self.root, SdkTemplate.ASSETS)

    @property
    def manifest(self):
        return os.path.join(self.root, SdkTemplate.MANIFEST)

    @property
    def game_smali_build_gradle(self):
        return os.path.join(self.root, SdkTemplate.SMALI_GRADLE_GAME)

    @property
    def channel_smali_build_gradle(self):
        return os.path.join(self.root, SdkTemplate.SMALI_GRADLE_CHANNEL)


    @property
    def fusion_smali_build_gradle(self):
        return os.path.join(self.root, SdkTemplate.SMALI_GRADLE_FUSION)

    @property
    def root_smali_build_gradle(self):
        return os.path.join(self.root, SdkTemplate.SMALI_GRADLE_ROOT)

    @property
    def game_build_gradle(self):
        return os.path.join(self.root, SdkTemplate.GRADLE_GAME)

    @property
    def channel_build_gradle(self):
        return os.path.join(self.root, SdkTemplate.GRADLE_CHANNEL)


    @property
    def fusion_build_gradle(self):
        return os.path.join(self.root, SdkTemplate.GRADLE_FUSION)

    @property
    def root_build_gradle(self):
        return os.path.join(self.root, SdkTemplate.GRADLE_ROOT)


class App:
    """
    smali方式打包使用到的目录结构 sdk + game res
    """
    def __init__(self, root, game_name, fusion_name, official_name, channel_name, dependence_folder_name):
        self.root = root
        self.app = os.path.join(root, "app")
        self.game_moudle = AndroidMoudle(self.app, game_name)
        self.dependence_folder = DependenciesFolder(self.app, dependence_folder_name)
        self.channel_sdk_moudle = None
        if channel_name:
            self.channel_sdk_moudle = AndroidMoudle(self.app, channel_name)

    def __str__(self):
        return self.app

    @property
    def build_gradle(self):
        return os.path.join(self.app, "build.gradle")

    @property
    def config_gradle(self):
        return os.path.join(self.app, "config.gradle")

    @property
    def gradle_properties(self):
        return os.path.join(self.app, "gradle.properties")

    @property
    def local_properties(self):
        return os.path.join(self.app, "local.properties")

    @property
    def proguard(self):
        return os.path.join(self.app, "proguard.txt")

    @property
    def settings_gradle(self):
        return os.path.join(self.app, "settings.gradle")

    def move_libs_to_dependence_folder(self):
        if self.channel_sdk_moudle:
            self._move(self.channel_sdk_moudle.libs)

    def _move(self, libs_path):
        logger = Logger()
        if not os.path.exists(libs_path):
            return
        for libfile in os.listdir(libs_path):
            if libfile.endswith(".jar") or libfile.endswith(".aar"):
                dependence_folder_lib = os.path.join(str(self.dependence_folder), libfile)
                if os.path.exists(dependence_folder_lib):
                    os.remove(dependence_folder_lib)
                    logger.info("文件 %s 已存在，删除文件" % dependence_folder_lib)
                if not os.path.exists(str(self.dependence_folder)):
                    os.mkdir(str(self.dependence_folder))
                shutil.move(os.path.join(libs_path, libfile), dependence_folder_lib)
                logger.info("移动文件 %s 到 %s" % (os.path.join(libs_path, libfile), dependence_folder_lib))


class AndroidMoudle:

    MANIFEST = "src/main/AndroidManifest.xml"
    RES = "src/main/res"
    LIBS = "libs"
    SRC = "src/main/java"
    ASSETS = "src/main/assets"

    def __init__(self, root, moudle_name):
        self.root = root
        self.moudle_name = moudle_name

    def __str__(self):
        return os.path.join(self.root, self.moudle_name)

    @property
    def name(self):
        return self.moudle_name

    @property
    def res(self):
        return os.path.join(str(self), AndroidMoudle.RES)

    @property
    def libs(self):
        return os.path.join(str(self), AndroidMoudle.LIBS)

    @property
    def src(self):
        return os.path.join(str(self), AndroidMoudle.SRC)

    @property
    def assets(self):
        return os.path.join(str(self), AndroidMoudle.ASSETS)

    @property
    def manifest(self):
        return os.path.join(str(self), AndroidMoudle.MANIFEST)

    @property
    def build_gradle(self):
        return os.path.join(str(self), "build.gradle")

    @property
    def proguard(self):
        return os.path.join(str(self), "proguard.txt")

    @property
    def build_outputs(self):
        return os.path.join(str(self), "build", "outputs")

    @property
    def assets_channelproperties(self):
        return os.path.join(self.assets, "channel.properties")

    def copy_template(self, sdk_template):
        if os.path.exists(sdk_template.res):
            shutil.copytree(sdk_template.res, self.res)
        if os.path.exists(sdk_template.src):
            shutil.copytree(sdk_template.src, self.src)
        if os.path.exists(sdk_template.libs):
            shutil.copytree(sdk_template.libs, self.libs)
        if os.path.exists(sdk_template.libs_predex):
            for file in os.listdir(sdk_template.libs_predex):
                shutil.copyfile(os.path.join(sdk_template.libs_predex, file), os.path.join(self.libs, file))

        if os.path.exists(sdk_template.assets):
            shutil.copytree(sdk_template.assets, self.assets)

        if os.path.exists(sdk_template.manifest):
            shutil.copy(sdk_template.manifest, self.manifest)
        pass


class DependenciesFolder:

    def __init__(self, root, folder_name):
        self.root = root
        self.f_name = folder_name

    def __str__(self):
        return os.path.join(self.root, self.folder_name)

    @property
    def folder_name(self):
        return self.f_name
