enum FileState {
    DEFAULT = 0,
    DOWNLOADING = 1,
    QUEUED = 2,
    DOWNLOADED = 3,
    DELETED = 4,
    EXTRACTING = 5,
    EXTRACTED = 6,
    ARCHIVED = 7 // Downloaded but moved locally
} 