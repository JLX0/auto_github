from LLM_utils.storage import Storage_base

class Storage(Storage_base):

    def __init__(self, path, repo_path,debug=False):
        super().__init__(path,debug)
        self.repo_path = repo_path
        self.add_repo_path()

    @Storage_base.auto_load_save
    def add_repo_path(self):
        if self.debug:
            print("checking repo entry in info")
        if self.repo_path not in self.information:
            if self.debug:
                print("adding repo entry in info")
            self.information[self.repo_path] = {}
        else:
            if self.debug:
                print("repo entry already exists")

    @Storage_base.auto_load_save
    def add_readme(self, readme):
        self.information[self.repo_path]['readme'] = readme

    @Storage_base.auto_load_save
    def add_file_structure(self, file_structure):
        self.information[self.repo_path]['file_structure'] = file_structure

    @Storage_base.auto_load_save
    def add_file_contents(self, file_contents):
        self.information[self.repo_path]['file_contents'] = file_contents

    @Storage_base.auto_load_save
    def add_designated_entries(self , info_type , info_content , info_trial=None) :
        """
        This method adds designated entries to a repository in the info dictionary.

        Args:
            info_type (str): The type of information being added (e.g., 'readme', 'file_structure', etc.).
            info_content: The content of the information being added.
            info_trial (int, optional): The trial number for the information. If None, it will be auto-incremented.

        Returns:
            None
        """

        # Ensure the repository path exists in the information dictionary
        if self.repo_path not in self.information :
            self.information[self.repo_path] = { }

        # Ensure the info_type exists within the repository path
        if info_type not in self.information[self.repo_path] :
            self.information[self.repo_path][info_type] = { }

        # Check if the trial already exists
        if info_trial is not None and str(info_trial) in self.information[self.repo_path][
            info_type] :
            raise ValueError(
                f"This trial already exists for the repository {self.repo_path} and info type "
                f"{info_type}"
                )

        # If info_trial is None, auto-increment the trial number
        if info_trial is None :
            existing_trials = list(map(int , self.information[self.repo_path][info_type].keys()))
            if len(existing_trials) == 0 :
                info_trial = 1
            else :
                info_trial = max(existing_trials) + 1

        # Add the information to the designated trial
        self.information[self.repo_path][info_type][str(info_trial)] = info_content

if __name__ == "__main__":
    storage = Storage("info.json" , "repo_path")
    storage.add_repo_path()
    storage.add_readme("README.md")
    print(storage.information)