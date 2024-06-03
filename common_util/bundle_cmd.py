# -*- coding: utf-8 -*-


from common_util.common import Terminal



class BundleCMD(object):

    @classmethod
    def compileZip(cls, aapt2, res_path, output_zip_path):
        """
        将资源编译为 zip

        :param aapt2: aapt2
        :param res_path: 资源文件夹
        :param output_zip_path: 生成资源的 zip

        [ aapt2 文件] compile --dir [ res 路径] -o [生成资源的 .zip ]
        """
        cmd = "{0} compile --dir \"{1}\" -o \"{2}\"".format(
             aapt2, res_path, output_zip_path)

        return Terminal.getstatusoutput(cmd)
    
    @classmethod
    def linkRes(cls, aapt2, zip_path, android_jar, manifest_file, min_ver, target_ver, compile_ver, ver_code, ver_name, output_base_apk):
        """
        链接资源(AAPT2 会将各种编译后的资源链接到一个 APK 中)

        :param zip_path: 资源的 .zip
        :param output_base_apk: 输出的 base.apk 路径
        :param android_jar: android.jar 文件
        :param manifest_file: manifest 文件
        :param min_ver: 最小版本
        :param target_ver: 目标版本
        :param ver_code: 版本号
        :param ver_name: 版本名

        [ aapt2 文件] link --proto-format [资源的 zip ] -o [输出的 base.apk] -I [ android.jar 文件] --manifest [ manifest 文件] --min-sdk-version [最小版本] --target-sdk-version [目标版本] --version-code [版本号] --version-name [版本名] --auto-add-overlay --replace-version
        
        2023/09/14 新增 --replace-version ：如果指定了 --version-code、--version-name 或 --revision-code，这些值将替换清单中已有的任何值。默认情况下，如果清单已经定义这些属性，则不会有任何变化。
        """
        cmd = "{0} link --proto-format \"{1}\" -o \"{2}\" -I \"{3}\" --manifest \"{4}\" --min-sdk-version {5} --target-sdk-version {6} --version-code {7} --version-name {8} --compile-sdk-version-name {9} --auto-add-overlay --replace-version".format( 
             aapt2, zip_path, output_base_apk, android_jar, manifest_file, min_ver, target_ver, ver_code, ver_name, compile_ver)

        return Terminal.getstatusoutput(cmd)

    @classmethod
    def linkResByDir(cls, aapt2, android_jar, manifest_file, output_base_apk):
        """
        链接资源(AAPT2 会将各种编译后的资源链接到一个 APK 中)
        :param aapt2: aapt2
        :param output_base_apk: 输出的 base.apk
        :param manifest_file: 文件
        :param android_jar: android.jar

        [ aapt2 文件] link --proto-format [资源的 dir ] -o [输出的 base.apk] -I [ android.jar 文件] --auto-add-overlay
        """
        cmd = "{0} link --proto-format -o {1} -I {2} --manifest {3} --auto-add-overlay".format(
             aapt2, output_base_apk, android_jar, manifest_file)

        return Terminal.getstatusoutput(cmd)

    @classmethod
    def signBundle(cls, jar_signer, aab_file, keystore, store_password, key_password, alias):
        """
        签名aab

        jarsigner -digestalg SHA1 -sigalg SHA1withRSA -keystore [keystore 文件] -storepass [store password] -keypass [key password] [aab 文件] [store alias]
        """
        cmd = "jarsigner -digestalg SHA1 -sigalg SHA1withRSA -keystore {0} -storepass {1} -keypass {2} {3} {4}".format(
            keystore, store_password, key_password, aab_file, alias)

        return Terminal.getstatusoutput(cmd)


    @classmethod
    def smali2dex(cls, smali_jar_path, smali_dir, dex_path):
        """
        smali 文件夹转 .dex 文件

        :param smali_jar_path: smali.jar 路径
        :param dex_path: 输出的 .dex 文件
        :param smali_dir: smali 文件夹

        java -jar [ smali.jar ] assemble -o [ .dex 文件] [ smali 文件夹]
        """
        cmd = "java -jar \"{0}\" assemble -o \"{1}\" \"{2}\"".format(
            smali_jar_path, dex_path, smali_dir)
        return Terminal.getstatusoutput(cmd)

    @classmethod
    def buildBundle(cls, bundle_tool_path, base_zip, output_aab):
        """
        构建 appbundle 

        :param bundle_tool_path: bundletool.jar 路径
        :param base_zip:  base.zip 文件
        :param output_aab:  输出的 .aab 

        java -jar [ bundletool.jar ] build-bundle --modules [ base.zip 文件] --output=[输出的 .aab ]
        """
        cmd = "java -jar \"{0}\" build-bundle --modules \"{1}\" --output=\"{2}\"".format(
            bundle_tool_path, base_zip, output_aab)
        return Terminal.getstatusoutput(cmd)
    
    @classmethod
    def gradleBundle(cls):
        """
        Gradle 打包

        win: gradle.bat bundle
        linux: gradle bundle
        
        """
        cmd = "gradle bundleRelease"
        return Terminal.getstatusoutput(cmd)

    @classmethod
    def aab2Apks(cls, bundletool_path, aab_path, output_apks_path, keystore_config):
        """
        .aab 转 .apks

        :param aab_path: aab 文件路径
        :param bundletool_path: bundletool 文件路径
        :param keystore_config: keystore 配置

        java -jar [ bundletool 文件] build-apks --bundle [ .aab 文件] --output [ .apks 文件]
            --ks=[签名文件]
            --ks-pass=pass:[签名密码]
            --ks-key-alias=[别名]
            --key-pass=pass:[别名密码]
        """

        keystore_str = ""
        if keystore_config:
            keystore_str = " --ks=\"{0}\" --ks-pass=pass:{1} --ks-key-alias={2} --key-pass=pass:{3}".format(
                keystore_config["store_file"], keystore_config["store_password"], keystore_config["key_alias"], keystore_config["key_password"])
        cmd = "java -jar \"{0}\" build-apks --bundle \"{1}\" --output \"{2}\" {3}".format(
            bundletool_path, aab_path, output_apks_path, keystore_str)
        return Terminal.getstatusoutput(cmd)