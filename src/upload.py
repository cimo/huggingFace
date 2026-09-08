import sys
sys.dont_write_bytecode = True

import os
import getpass
import hashlib
import json
from huggingface_hub import HfApi
from huggingface_hub.hf_api import RepoFile

class HuggingFaceUpload:
    def _cacheSave(self):
        with open(f"{self.pathCache}upload.json", "w", encoding="utf-8") as output:
            json.dump(self.cacheObject, output, ensure_ascii=False)

    def _hashFile(self, pathFile, isLfs):
        modificationTime = os.path.getmtime(pathFile)

        if pathFile in self.cacheObject:
            cacheFileObject = self.cacheObject[pathFile]

            if cacheFileObject["modificationTime"] == modificationTime and cacheFileObject["isLfs"] == isLfs:
                return cacheFileObject["hash"]

        if isLfs == True:
            hashObject = hashlib.sha256()
        else:
            hashObject = hashlib.sha1()
            hashObject.update(f"blob {os.path.getsize(pathFile)}\0".encode())

        with open(pathFile, "rb") as file:
            chunk = file.read(1024 * 1024)

            while chunk:
                hashObject.update(chunk)

                chunk = file.read(1024 * 1024)

        self.cacheObject[pathFile] = {"modificationTime": modificationTime, "isLfs": isLfs, "hash": hashObject.hexdigest()}

        self._cacheSave()

        return self.cacheObject[pathFile]["hash"]

    def _uploadCheck(self, pathFile, pathRelative, remoteFileObject):
        if pathRelative not in remoteFileObject:
            return True

        remoteFile = remoteFileObject[pathRelative]

        if remoteFile.lfs:
            if self._hashFile(pathFile, True) != remoteFile.lfs.sha256:
                return True
        else:
            if self._hashFile(pathFile, False) != remoteFile.blob_id:
                return True

        return False

    def execute(self):
        directoryList = sorted(os.listdir(self.pathModel))

        for a in range(len(directoryList)):
            if os.path.isdir(f"{self.pathModel}{directoryList[a]}"):
                pathRepository = f"{self.pathModel}{directoryList[a]}/"
                repositoryId = f"{self.author}/{directoryList[a]}"
                remoteFileObject = {}

                for entry in self.api.list_repo_tree(repo_id=repositoryId, repo_type="model", recursive=True):
                    if isinstance(entry, RepoFile):
                        remoteFileObject[entry.path] = entry

                for pathCurrent, directoryWalkList, fileList in os.walk(pathRepository):
                    if ".git" in directoryWalkList:
                        directoryWalkList.remove(".git")

                    for b in range(len(fileList)):
                        pathFile = os.path.join(pathCurrent, fileList[b])
                        pathRelative = os.path.relpath(pathFile, pathRepository)

                        if self._uploadCheck(pathFile, pathRelative, remoteFileObject) == True:
                            print(f"Upload {repositoryId}: {pathRelative}")

                            self.api.upload_file(
                                path_or_fileobj=pathFile,
                                path_in_repo=pathRelative,
                                repo_id=repositoryId,
                                repo_type="model",
                                commit_message="update"
                            )

        print("Upload completed.")

    def __init__(self):
        self.author = "cimo001"
        self.pathSrc = f"{os.path.dirname(os.path.abspath(__file__))}/"
        self.pathModel = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/model/"
        self.pathCache = f"{self.pathSrc}cache/"
        self.cacheObject = {}

        os.makedirs(self.pathCache, exist_ok=True)

        if os.path.isfile(f"{self.pathCache}upload.json"):
            with open(f"{self.pathCache}upload.json", "r", encoding="utf-8") as input:
                self.cacheObject = json.load(input)

        self.token = getpass.getpass("Insert your token: ")
        self.api = HfApi(token=self.token)

huggingFaceUpload = HuggingFaceUpload()
huggingFaceUpload.execute()
