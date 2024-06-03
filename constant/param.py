class CmdParam:
    class COMMAND:
        APK2AAB = "apk2aab"

    class OPTIONS:
        DEBUG = "--debug"
        KEEP = "--keeptmp"

    class ARGS:
        SRC = "SRC"
        CONF = "CONF"
        OUT = "OUT"
        WORKSPACE = "--workspace"

class PackParam:

    GAME_LABEL = "game_label"   # 游戏标识
    SDK_LABEL = "sdk_label"     # SDK标识

    PACKAGE_NAME = "package_name" # 包名

    ANDROID_BUILD_TOOL = "build_version"  # 使用的Android SDK Build Tool 工具版本

    COMPILE_VERSION = "compile_version"  # 指定Android SDK编译版本
    MIN_SDK_VERSION = "min_sdkversion"  # 支持的最小的Android SDK版本
    MAX_SDK_VERSION = "max_sdkversion"  # 支持的最大的Android SDK版本
    TARGET_SDK_VERSION = "target_sdkversion"  # 目标编译版本

    KEY_STORE_NAME = "keystore_name"
    KEY_STORE_KEYPASS = "keystore_keypass"
    KEY_STORE_ALIAS = "keystore_alias"
    KEY_STORE_STOREPASS = "keystore_storepass"

    VERSION_NAME = "version_name"
    VERSION_CODE = "version_code"

    EXTRA_CMD = "extra_cmd"     # 参数覆盖，优先级最高

class Apk2AabEnvirParam:
    CHANNEL_EXTRA_SCRIPTS = "path.script.channel"
    GAME_EXTRA_SCRIPTS = "path.script.game"
    GAME_CHANNEL_EXTRA_SCRIPTS = "path.script.game_channel"
    
    APK_TOOL = "path.apktool"
    BUNDLE_TOOL = "path.bundletool"
    SMALI_JAR = "path.smali_jar"
    TEMP_MANIFEST = "path.temp_manifest"     # 重打包时用到的manifest模板路径
    AAPT2 = "path.android.aapt2"               
    ANDROID_JAR = "path.android.android_jar"
    APK_SIGNER = "path.android.apksigner"
    JAR_SIGNER = "path.android.jarsigner"
    ZIPALIGN = "path.android.zipalign"

    ASSETS_MODULE_NAME = "assets_module_name"   # assets模块名称
    COMPILE_SDK_VERSION = "compileSdkVersion"   # 编译SDK版本
    COMPILE_SDK_VERSION_CODE_NAME = "compileSdkVersionCodename"   # 编译SDK版本代号
    PLATFORM_BUILD_VERSION_CODE = "platformBuildVersionCode"   # 平台SDK版本
    PLATFORM_BUILD_VERSION_NAME = "platformBuildVersionName"   # 平台SDK版本代号


class Apk2AabParam:
    ASSESTS_SPACIAL_FILES = "assets_spcial_files"

    CHANNEL_EXTRA_SCRIPTS = "path.script.channel"
    GAME_EXTRA_SCRIPTS = "path.script.game"
    GAME_CHANNEL_EXTRA_SCRIPTS = "path.script.game_channel"
