"use client";

import { useState, useEffect } from "react";
import { projectService } from "../../services/projectService";
import {
  FileCode,
  Download,
  Copy,
  Check,
  RefreshCw,
  FolderOpen,
} from "lucide-react";

interface WorkspaceFile {
  relative_path?: string;
  file_path?: string;
  size_bytes?: number;
  sha256?: string;
  file_hash?: string;
}

interface FileExplorerProps {
  projectId: string;
}

export default function FileExplorer({ projectId }: FileExplorerProps) {
  const [files, setFiles] = useState<WorkspaceFile[]>([]);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [loadingList, setLoadingList] = useState(true);
  const [loadingFile, setLoadingFile] = useState(false);
  const [copied, setCopied] = useState(false);

  const getFilePath = (file: WorkspaceFile) =>
    file.relative_path || file.file_path || "";

  const getFileHash = (file?: WorkspaceFile) =>
    file?.sha256 || file?.file_hash || "";

  const fetchFileList = async () => {
    try {
      setLoadingList(true);
      const list = await projectService.getFiles(projectId);
      setFiles(list);
      if (list.length > 0) {
        const firstPath = getFilePath(list[0]);
        if (firstPath) {
          handleSelectFile(firstPath);
        }
      }
    } catch (err) {
      console.error("Failed to fetch workspace files:", err);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    fetchFileList();
  }, [projectId]);

  const handleSelectFile = async (path: string) => {
    try {
      setSelectedPath(path);
      setLoadingFile(true);
      const content = await projectService.readFile(projectId, path);
      setFileContent(content);
    } catch (err) {
      console.error(`Failed to read file ${path}:`, err);
      setFileContent("# Error reading file from workspace.");
    } finally {
      setLoadingFile(false);
    }
  };

  const handleCopy = () => {
    if (!fileContent) return;
    navigator.clipboard.writeText(fileContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const selectedMeta = files.find((f) => getFilePath(f) === selectedPath);
  const selectedHash = getFileHash(selectedMeta);

  return (
    <div className="space-y-4">
      {/* Top Header */}
      <div className="p-4 bg-white border border-border rounded-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-medium text-black">
            Generated Project Workspace
          </h3>
          <p className="text-xs text-grey-500 font-light">
            Browse source code, database migrations, scaffolding, and Docker configurations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchFileList}
            className="p-2 text-grey-500 hover:text-black rounded hover:bg-grey-100 transition-colors"
            title="Refresh File List"
          >
            <RefreshCw className={`w-4 h-4 ${loadingList ? "animate-spin" : ""}`} />
          </button>

          <a
            href={projectService.getExportUrl(projectId)}
            download
            className="inline-flex items-center gap-2 bg-black text-white hover:bg-grey-800 text-xs font-medium px-4 py-2 rounded-md transition-all shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Project ZIP</span>
          </a>
        </div>
      </div>

      {loadingList ? (
        <div className="py-20 text-center text-xs font-mono text-grey-500">
          <RefreshCw className="w-4 h-4 animate-spin mx-auto mb-2 text-black" />
          Loading workspace files...
        </div>
      ) : files.length === 0 ? (
        <div className="p-12 text-center bg-grey-50 border border-dashed border-border rounded-lg space-y-2">
          <FolderOpen className="w-8 h-8 mx-auto text-grey-400" />
          <h4 className="text-sm font-medium text-black">No files generated yet</h4>
          <p className="text-xs text-grey-500 max-w-sm mx-auto font-light">
            Trigger code generation from the project workflow to synthesize backend and frontend source files.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* File Tree / List */}
          <div className="lg:col-span-1 bg-white border border-border rounded-lg p-3 max-h-[640px] overflow-y-auto space-y-1">
            <div className="text-[11px] font-mono uppercase text-grey-400 px-2 py-1 tracking-wider flex items-center justify-between">
              <span>Files ({files.length})</span>
            </div>
            {files.map((file) => {
              const filePath = getFilePath(file);
              return (
                <button
                  key={filePath}
                  onClick={() => handleSelectFile(filePath)}
                  className={`w-full text-left px-3 py-2 rounded-md text-xs font-mono flex items-center justify-between gap-2 transition-colors ${
                    selectedPath === filePath
                      ? "bg-black text-white"
                      : "text-grey-700 hover:bg-grey-50"
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <FileCode
                      className={`w-3.5 h-3.5 shrink-0 ${
                        selectedPath === filePath
                          ? "text-white"
                          : "text-grey-400"
                      }`}
                    />
                    <span className="truncate">{filePath}</span>
                  </div>
                  {file.size_bytes !== undefined && (
                    <span className="text-[10px] opacity-60 shrink-0">
                      {(file.size_bytes / 1024).toFixed(1)}k
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Code Viewer */}
          <div className="lg:col-span-2 bg-grey-900 text-grey-100 rounded-xl overflow-hidden border border-grey-800 flex flex-col h-[640px] shadow-sm">
            {/* Header */}
            <div className="px-4 py-3 bg-grey-950 border-b border-grey-800 flex items-center justify-between text-xs font-mono text-grey-400">
              <span className="truncate text-grey-200">
                {selectedPath || "Select a file to view"}
              </span>
              <div className="flex items-center gap-4 shrink-0">
                {selectedHash && (
                  <span className="text-[10px] text-grey-500 hidden sm:inline">
                    SHA256: {selectedHash.slice(0, 10)}...
                  </span>
                )}
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 hover:text-white transition-colors"
                  title="Copy code"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-[11px] text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span className="text-[11px]">Copy</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Code Body */}
            <div className="flex-1 overflow-auto p-4 text-xs font-mono leading-relaxed bg-grey-900 text-grey-200">
              {loadingFile ? (
                <div className="py-20 text-center text-grey-500">
                  <RefreshCw className="w-4 h-4 animate-spin mx-auto mb-2" />
                  Loading file content...
                </div>
              ) : (
                <pre className="whitespace-pre">
                  {fileContent || "Select a file to inspect its source code."}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
