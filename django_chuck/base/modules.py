import os
import imp
import shutil
from random import choice
from django_chuck.exceptions import ModuleError
from django_chuck import utils


class BaseModule(object):

    def __init__(self, module_name, args, cfg, module_dir=None):
        self.cfg = cfg
        self.args = args

        if module_dir:
            self.dir = module_dir
        else:
            for module_basedir in self.module_basedirs:
                for module in os.listdir(module_basedir):
                    module_dir = os.path.join(module_basedir, module_name)
                    if os.path.isdir(module_dir):
                        self.dir = module_dir
                        break

        if not self.dir:
            raise ModuleError("Cannot find module " + module_name)

        self.name = module_name
        meta_file = os.path.join(self.dir, "chuck_module.py")

        if os.access(meta_file, os.R_OK):
            self.meta_data = imp.load_source(self.name.replace("-", "_"), meta_file)
        else:
            self.meta_data = None


    def arg_or_cfg(self, var):
        return utils.arg_or_cfg(var, self.args, self.cfg)


    def __getattr__(self, name):
        """
        Get value either from command-line argument or config setting
        """
        return utils.get_property(name, self.args, self.cfg)


    def install(self, **kwargs):
        """
        Install the module.
        Exec post build hook if exec_post_build is True
        """

        utils.print_header("BUILDING " + self.name)

        # For each file in the module dir
        for f in utils.get_files(self.dir):
            if not "chuck_module.py" in f:
                # Absolute path to module file
                input_file = f

                # Relative path to module file
                rel_path_old = f.replace(self.dir, "")

                # Relative path to module file with project_name replaced
                rel_path_new = f.replace(self.dir, "").replace("project", self.project_name.replace("-", "_"))

                # Absolute path to module file in site dir
                output_file = f.replace(self.dir, self.site_dir).replace(rel_path_old, rel_path_new)

                # Apply templates
                print "\t%s -> %s" % (input_file, output_file)
                placeholder = utils.get_placeholder(self.args, self.cfg)
                utils.compile_template(input_file, output_file, placeholder, self.site_dir, self.project_dir, self.template_engine, self.debug)

        if self.name == "core":
            secret_key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@%^&*(-_=+)') for i in range(50)])
            utils.append_to_file(os.path.join(self.project_dir, "settings", "common.py"), "\nSECRET_KEY = '" + secret_key + "'\n")

            if os.access(os.path.join(self.site_dir, ".gitignore_" + self.project_name), os.R_OK):
                shutil.move(os.path.join(self.site_dir, ".gitignore_" + self.project_name), os.path.join(self.site_dir, ".gitignore"))

        # Shall we execute module post build action?
        if kwargs.get("exec_post_build", False) and hasattr(self, "post_build"):
            self.meta_data = utils.inject_variables_and_functions(self.meta_data, self.args, self.cfg)
            self.meta_data.post_build()



    #
    # GET META DATA
    #
    def get_priority(self):
        if self.meta_data and hasattr(self.meta_data, 'priority'):
            return self.meta_data.priority
        return 100000
    priority = property(get_priority)

    def get_dependencies(self):
        if self.meta_data and hasattr(self.meta_data, 'depends'):
            return self.meta_data.depends
        return None
    dependencies = property(get_dependencies)

    def get_incompatibles(self):
        if self.meta_data and hasattr(self.meta_data, 'incompatible_with'):
            return self.meta_data.incompatible_with
        return None
    incompatibles = property(get_incompatibles)

    def get_description(self):
        if self.meta_data and hasattr(self.meta_data, 'description'):
            return self.meta_data.description
        return ""
    description = property(get_description)

    def get_post_build(self):
        if self.meta_data and hasattr(self.meta_data, 'post_build'):
            return self.meta_data.post_build
        return None
    post_build = property(get_post_build)

    def get_post_setup(self):
        if self.meta_data and hasattr(self.meta_data, 'post_setup'):
            return self.meta_data.post_build
        return None
    post_setup = property(get_post_setup)
