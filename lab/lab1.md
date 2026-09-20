\# Lab 1 - Git/DVC and Data Preparation



\## Solution Adopted



For the DVC remote, I adopted \*\*Solution 1: Use a local remote instead of DagsHub (recommended)\*\*.



The DVC remote was configured as:



`C:\\Users\\Maroun\\Desktop\\mlops-lab-1-dvc-storage`



This folder is outside the Git repository and stores the actual DVC-tracked data. GitHub stores the Git repository, source code, configuration, and DVC pointer files, while DVC manages the actual dataset.



\---



\## Question 1 - Observe the files created by `uv init`



After running `uv init`, the project contained files and folders such as:



\* `.python-version` - specifies the Python version used by the project.

\* `pyproject.toml` - contains project metadata and Python dependencies.

\* `uv.lock` - locks the exact dependency versions for reproducible environments.

\* `src/` - source-code directory for the project.

\* `README.md` - project documentation.



These files provide the initial Python project structure and allow the project's environment and dependencies to be reproduced.



\---



\## Question 2 - What files are created by `dvc init`?



Running `dvc init` created the DVC configuration structure, including:



\* `.dvc/` - contains DVC repository configuration.

\* `.dvc/config` - contains non-secret DVC configuration, including the configured remote.

\* `.dvc/.gitignore` - contains Git ignore rules used by DVC.

\* `.dvcignore` - specifies files that DVC should ignore when processing data.



The DVC configuration and pointer files needed to reproduce the project should be committed to Git. The actual dataset should not be committed to Git; it is stored and versioned by DVC.



\---



\## Question 3 - Where are credentials stored? What are the options other than `--global`? Should credentials be pushed to GitHub?



DVC supports different configuration scopes. The `--global` option stores configuration in the user's global DVC configuration. Repository-level configuration is stored in `.dvc/config`, while local repository configuration can be stored separately in `.dvc/config.local`.



Credentials such as usernames, passwords, access tokens, and other secrets should \*\*never be pushed to GitHub\*\*.



In this lab, I used a local DVC remote, so DagsHub authentication credentials were not required.



\---



\## Question 4 - What happened to `.gitignore` after `dvc add data`?



After running:



```bash

dvc add data

```



DVC added:



```text

/data

```



to `.gitignore`.



This prevents the actual `data` directory from being committed to Git. Instead, DVC creates a pointer file named `data.dvc` that identifies the corresponding version of the data.



\---



\## Question 5 - What does `data.dvc` contain?



The `data.dvc` file is a pointer to the data version managed by DVC.



For the initial raw dataset, it contained information such as:



```yaml

outs:

\- md5: a3a457d03c51ff8b037a833440f6ad13.dir

&#x20; size: 1188442712

&#x20; nfiles: 16643

&#x20; hash: md5

&#x20; path: data

```



The important information includes:



\* `md5` - identifies the content/version of the tracked data directory.

\* `size` - total size of the tracked data.

\* `nfiles` - number of tracked files.

\* `hash` - hashing method.

\* `path` - location of the data in the working directory.



When the processed datasets were added, DVC updated `data.dvc` with a new data hash representing the new version.



\---



\## Question 6 - Is the code/data on GitHub? Is there a pointer? What about the DVC remote?



The GitHub repository contains:



\* Project source code.

\* Python project configuration.

\* DVC configuration.

\* `.dvcignore`.

\* `.gitignore`.

\* `data.dvc`, which is the pointer to the dataset version.



The actual Food-11 dataset is \*\*not stored directly in GitHub\*\*.



The actual dataset is stored by DVC in the configured local DVC remote:



```text

C:\\Users\\Maroun\\Desktop\\mlops-lab-1-dvc-storage

```



Therefore, Git tracks the project and the data pointer, while DVC stores the actual data.



\---



\## Question 7 - What happens in a new clone?



I tested the workflow in a separate temporary directory.



After cloning the GitHub repository, the `data` directory was not present because the actual dataset is not stored in Git.



The command required to retrieve the DVC-tracked data was:



```bash

uv run dvc pull

```



The command successfully restored the dataset:



```text

A       data\\

16021 files fetched and 16643 files added

```



This demonstrates that cloning the Git repository retrieves the code and DVC pointer, while `dvc pull` retrieves the corresponding data from the DVC remote.



Because this lab uses a \*\*local DVC remote\*\*, the remote is available on the same computer but is not hosted publicly for other computers.



\---



\## Data Preparation



A Python script was created at:



```text

src/food11/data.py

```



The script:



1\. Reads the raw Food-11 dataset from `data/food11\_raw`.

2\. Uses the filename prefix to determine the category.

3\. Resizes images to `128x128`.

4\. Organizes images into category folders.

5\. Creates:



&#x20;  \* `data/food11\_processed`

&#x20;  \* `data/food11\_processed\_mini`

6\. Creates the mini dataset with a maximum of 100 images per category for each split.



The Food-11 categories used were:



1\. Bread

2\. Dairy product

3\. Dessert

4\. Egg

5\. Fried food

6\. Meat

7\. Noodles-Pasta

8\. Rice

9\. Seafood

10\. Soup

11\. Vegetable-Fruit



The processed images were verified to have size `128x128`.



The mini training dataset was verified to contain exactly 100 images in each of the 11 categories.



\---



\## Question 8 - Switching Between Data Versions



The Git history for `data.dvc` showed:



```text

fa4c752 Add food11\_processed and food11\_processed\_mini

5db01a2 Track Food-11 dataset with DVC

```



The older commit `5db01a2` represented the version containing only the raw dataset.



After running:



```bash

git checkout 5db01a2

uv run dvc checkout

```



the `data` directory contained only:



```text

food11\_raw

```



The folders:



```text

food11\_processed

food11\_processed\_mini

```



were no longer present.



This demonstrates that Git selects the appropriate version of the `data.dvc` pointer, while `dvc checkout` restores the corresponding version of the actual data.



Finally, I returned to the latest version:



```bash

git checkout main

uv run dvc checkout

```



The processed datasets were restored.



Therefore, the experiment demonstrates that Git and DVC work together: Git versions the code and DVC pointer, while DVC versions and restores the actual datasets.



\---



\## Final Git/DVC State



The final Git history includes:



```text

fa4c752 Add food11\_processed and food11\_processed\_mini

5db01a2 Track Food-11 dataset with DVC

9c60d58 Configure local DVC remote

9d62bf0 Initialize git and dvc

```



The final working tree was verified to be clean:



```text

nothing to commit, working tree clean

```



The processed data was successfully pushed to the local DVC remote:



```text

16014 files pushed

```



Thus, the Git/DVC setup and Food-11 data preparation requirements for Lab 1 were completed successfully.



