from dataclasses import dataclass
from typing import List, Optional, Tuple
import requests
from pathlib import Path
from src.misc import get_extension_from_url
from src import logger

@dataclass
class DownloadResult:
    success: bool
    content: Optional[bytes]
    error: Optional[str]   

    def __post_init__(self):
        if self.success and self.error:
            logger.warning("DownloadResult cannot be successful and have an error")
            raise ValueError("DownloadResult cannot be successful and have an error")
        if not self.success and not self.error:
            logger.warning("DownloadResult must have an error message if it is not successful")
            raise ValueError("DownloadResult must have an error message if it is not successful")

@dataclass
class DataSet:
    url: str
    metric: str
    gender: str
    age_range: str ## in year. use 0_5 for 0-5 years
    description: Optional[str] = '' 
    savepath: Path = Path(__file__).parent.parent / 'data'

    @property
    def filename(self) -> str:  
        return self.savepath / f'{self.metric}.{self.gender}.{self.age_range}.{get_extension_from_url(self.url)}'

    def save_content_to_file(self, content: DownloadResult) -> None:
        with open(self.filename, 'wb') as file:
            file.write(content.content)


class Downloader:
    def __init__(self, datasets: List[DataSet]):
        self.datasets = datasets 

    def download(self, dataset: DataSet) -> DownloadResult:
        """Download the dataset from the url and save it to the file system.
        If the download is successful, return a DownloadResult with success=True and the content of the file.
        If the download fails, return a DownloadResult with success=False and the error message.
        If dataset.filename already exists, do not download the file again.
        """
        if dataset.filename.exists():
            logger.warning(f"{dataset.filename} already exists. Skipping download")
            return DownloadResult(success=True, content=None, error=None)
        try:
            logger.debug(f"Downloading {dataset.metric} for {dataset.gender} ages {dataset.age_range} years from {dataset.url}")
            response = requests.get(dataset.url)
            response.raise_for_status()
            result = DownloadResult(success=True, content=response.content, error=None)
            dataset.save_content_to_file(result)
            return result
        except requests.exceptions.RequestException as e:
            res = DownloadResult(success=False, content=None, error=str(e))
            logger.error(f"Failed to download {dataset.filename}: {res.error}")
            return res
        
        except Exception as e:
            res = DownloadResult(success=False, content=None, error=str(e))
            logger.error(f"Failed to download {dataset.filename}: {res.error}")
            return res


    def download_all(self) -> List[Tuple[DataSet, DownloadResult]]:
        return [(dataset, self.download(dataset)) for dataset in self.datasets]
    
