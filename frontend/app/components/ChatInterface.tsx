"use client";

import {
  ChangeEvent,
  FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";

type DeveloperMode =
  | "explain_code"
  | "debug_code"
  | "generate_code"
  | "refactor_code"
  | "generate_documentation"
  | "explain_errors";

type InterfaceMode =
  | DeveloperMode
  | "document_qa"
  | "github_qa";

type Message = {
  id: number;
  role: "user" | "assistant";
  content: string;
};

type ChatResponse = {
  mode: DeveloperMode;
  message: string;
  response: string;
  status: string;
};

type UploadResponse = {
  document_id: string;
  filename: string;
  chunk_count: number;
  status: string;
};

type DocumentAnswer = {
  document_id: string;
  question: string;
  answer: string;
  status: string;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

const MODES: {
  value: InterfaceMode;
  label: string;
  description: string;
}[] = [
  {
    value: "explain_code",
    label: "Explain Code",
    description:
      "Understand what your code does and how it works.",
  },
  {
    value: "debug_code",
    label: "Debug Code",
    description:
      "Find bugs, understand their causes, and fix your code.",
  },
  {
    value: "generate_code",
    label: "Generate Code",
    description:
      "Create new code based on your requirements and specifications.",
  },
  {
    value: "refactor_code",
    label: "Refactor Code",
    description:
      "Improve code quality and maintainability while preserving functionality.",
  },
  {
    value: "generate_documentation",
    label: "Generate Documentation",
    description:
      "Create clear technical documentation from your code.",
  },
  {
    value: "explain_errors",
    label: "Explain Errors",
    description:
      "Understand error messages and learn how to fix them.",
  },
  {
    value: "document_qa",
    label: "Document Q&A",
    description:
      "Upload a text document and ask questions about its contents.",
  },
  {
    value: "github_qa",
    label: "GitHub Q&A",
    description:
      "Ask questions about your GitHub repository and its codebase.",
  }
];

const placeholderByMode: Record<
  InterfaceMode,
  string
> = {
  explain_code:
    "Paste your code here...",
  debug_code:
    "Paste the code you want to debug...",
  generate_code:
    "Describe what you want to build...",
  refactor_code:
    "Paste the code you want to refactor...",
  generate_documentation:
    "Paste the code you want to document...",
  explain_errors:
    "Paste the error message, stack trace, or related code...",
  document_qa:
    "Ask a question about your uploaded document...",
  github_qa:
    "Ask a question about the GitHub repository...",
};

const buttonLabelByMode: Record<
  InterfaceMode,
  string
> = {
  explain_code: "Explain Code",
  debug_code: "Debug Code",
  generate_code: "Generate Code",
  refactor_code: "Refactor Code",
  generate_documentation: "Generate Docs",
  explain_errors: "Explain Error",
  document_qa: "Ask Document",
  github_qa: "Ask Repository",
};

export default function ChatInterface() {
  const [mode, setMode] =
    useState<InterfaceMode>("explain_code");

  const [input, setInput] = useState("");

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [isLoading, setIsLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [documentId, setDocumentId] =
    useState<string | null>(null);

  const [documentName, setDocumentName] =
    useState("");

  const [githubUrl, setGithubUrl] =
    useState("");

  const [githubRepository, setGithubRepository] =
    useState("");

  const [isIndexingGithub, setIsIndexingGithub] =
    useState(false);

  const [githubIndexed, setGithubIndexed] =
    useState(false);

  const [isUploading, setIsUploading] =
    useState(false);

  const fileInputRef =
    useRef<HTMLInputElement>(null);

  const messagesEndRef =
    useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  const selectedMode = MODES.find(
    (item) => item.value === mode
  );

  async function handleDocumentUpload(
    event: ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setError("");
    setIsUploading(true);

    try {
      const formData = new FormData();

      formData.append("file", file);

      const response = await fetch(
        `${API_URL}/api/v1/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Unable to upload the document."
        );
      }

      const uploadResponse =
        data as UploadResponse;

      setDocumentId(
        uploadResponse.document_id
      );

      setDocumentName(
        uploadResponse.filename
      );

      setMessages([]);

      setInput("");

    } catch (uploadError) {
      const message =
        uploadError instanceof Error
          ? uploadError.message
          : "Unable to upload the document.";

      setError(message);

      setDocumentId(null);
      setDocumentName("");

    } finally {
      setIsUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

    async function handleGithubIndex() {
    const trimmedUrl = githubUrl.trim();

    if (!trimmedUrl) {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    setError("");
    setIsIndexingGithub(true);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/github/index`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repository_url: trimmedUrl,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Unable to index the GitHub repository."
        );
      }
      setGithubRepository(data.repository);
      setGithubIndexed(true);
      setMessages([]);
      setInput("");
    } catch (githubError) {
      const message =
        githubError instanceof Error
          ? githubError.message
          : "Unable to index the GitHub repository.";

      setError(message);
      setGithubIndexed(false);
    } finally {
      setIsIndexingGithub(false);
    }
  }

  function handleModeChange(
    nextMode: InterfaceMode
  ) {
    setMode(nextMode);
    setError("");
    setInput("");

    if (nextMode !== "document_qa") {
      setDocumentId(null);
      setDocumentName("");
    }
    if (nextMode !== "github_qa") {
      setGithubUrl("");
      setGithubRepository("");
      setGithubIndexed(false);
    }

    setMessages([]);
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    const trimmedInput =
      input.trim();

    if (
      !trimmedInput ||
      isLoading ||
      isUploading
    ) {
      return;
    }

    if (
      mode === "document_qa" &&
      !documentId
    ) {
      setError(
        "Please upload a document before asking a question."
      );

      return;
    }
    if (
  mode === "github_qa" &&
  !githubIndexed
) {
  setError(
    "Please index a GitHub repository before asking a question."
  );

  return;
}

    setError("");

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: trimmedInput,
    };

    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    setInput("");
    setIsLoading(true);

    try {
      let assistantContent = "";

      if (mode === "document_qa") {
        const response = await fetch(
          `${API_URL}/api/v1/documents/ask`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              document_id: documentId,
              question: trimmedInput,
            }),
          }
        );

        const data =
          await response.json();

        if (!response.ok) {
          throw new Error(
            data?.detail ||
              "Unable to answer the document question."
          );
        }

        const documentResponse =
          data as DocumentAnswer;

        assistantContent =
          documentResponse.answer;

      } 
      else if (mode === "github_qa") {
        const response = await fetch(
          `${API_URL}/api/v1/github/ask`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              repository: githubRepository,
              question: trimmedInput,
            }),
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data?.detail ||
              "Unable to answer the GitHub repository question."
          );
        }

        assistantContent =
          data.answer;
      }
      else {
        const response = await fetch(
          `${API_URL}/api/v1/chat`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              mode,
              message: trimmedInput,
            }),
          }
        );

        const data =
          await response.json();

        if (!response.ok) {
          throw new Error(
            data?.detail ||
              "The AI service is currently unavailable."
          );
        }

        const chatResponse =
          data as ChatResponse;

        assistantContent =
          chatResponse.response;
      }

      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content: assistantContent,
      };

      setMessages((current) => [
        ...current,
        assistantMessage,
      ]);

    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : "Something went wrong.";

      setError(message);

    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-64px)] flex-col">
      <div className="border-b border-white/10 bg-black/20 px-4 py-4">
        <div className="mx-auto max-w-5xl">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-lg font-semibold text-white">
                Nexkora Developer Assistant
              </h1>

              <p className="mt-1 text-sm text-zinc-400">
                AI-powered tools for understanding and working with code.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <label
                htmlFor="developer-mode"
                className="text-sm text-zinc-400"
              >
                Mode
              </label>

              <select
                id="developer-mode"
                value={mode}
                onChange={(event) =>
                  handleModeChange(
                    event.target
                      .value as InterfaceMode
                  )
                }
                disabled={
                  isLoading ||
                  isUploading
                }
                className="rounded-lg border border-white/10 bg-zinc-900 px-3 py-2 text-sm text-white outline-none transition focus:border-white/30 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {MODES.map((item) => (
                  <option
                    key={item.value}
                    value={item.value}
                  >
                    {item.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {selectedMode && (
            <p className="mt-3 text-sm text-zinc-500">
              {selectedMode.description}
            </p>
          )}
        </div>
      </div>

      {mode === "document_qa" && (
        <div className="border-b border-white/10 bg-black/10 px-4 py-4">
          <div className="mx-auto max-w-5xl">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-medium text-zinc-200">
                  Document
                </p>

                {documentName ? (
                  <p className="mt-1 text-xs text-zinc-500">
                    {documentName}
                  </p>
                ) : (
                  <p className="mt-1 text-xs text-zinc-600">
                    No document uploaded.
                  </p>
                )}
              </div>

              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.md,text/plain,text/markdown"
                  onChange={
                    handleDocumentUpload
                  }
                  disabled={
                    isUploading ||
                    isLoading
                  }
                  className="hidden"
                />

                <button
                  type="button"
                  onClick={() =>
                    fileInputRef.current?.click()
                  }
                  disabled={
                    isUploading ||
                    isLoading
                  }
                  className="rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-zinc-200 transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {isUploading
                    ? "Uploading..."
                    : documentId
                      ? "Replace Document"
                      : "Upload Document"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
            {mode === "github_qa" && (
        <div className="border-b border-white/10 bg-black/10 px-4 py-4">
          <div className="mx-auto max-w-5xl">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <div className="flex-1">
                <label
                  htmlFor="github-url"
                  className="mb-2 block text-sm font-medium text-zinc-200"
                >
                  GitHub Repository
                </label>

                <input
                  id="github-url"
                  type="url"
                  value={githubUrl}
                  onChange={(event) =>
                    setGithubUrl(event.target.value)
                  }
                  placeholder="https://github.com/username/repository"
                  disabled={
                    isIndexingGithub ||
                    isLoading
                  }
                  className="w-full rounded-lg border border-white/10 bg-zinc-900 px-4 py-2 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-white/30 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>

              <button
                type="button"
                onClick={handleGithubIndex}
                disabled={
                  isIndexingGithub ||
                  isLoading ||
                  githubUrl.trim().length === 0
                }
                className="rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-zinc-200 transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-40"
              >
                {isIndexingGithub
                  ? "Indexing..."
                  : githubIndexed
                    ? "Re-index Repository"
                    : "Index Repository"}
              </button>
            </div>

            {githubIndexed && (
              <p className="mt-2 text-xs text-green-400">
                Repository indexed successfully. You can now ask questions about it.
              </p>
            )}
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="mx-auto max-w-5xl space-y-5">
          {messages.length === 0 && (
            <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.02] p-8 text-center">
              <h2 className="text-base font-medium text-zinc-200">
                {selectedMode?.label}
              </h2>

              <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-zinc-500">
                {selectedMode?.description}
              </p>

              {mode === "document_qa" &&
                !documentId && (
                  <p className="mt-4 text-xs text-zinc-600">
                    Upload a .txt or .md file to get started.
                  </p>
                )}
                {mode === "github_qa" &&
  !githubIndexed && (
    <p className="mt-4 text-xs text-zinc-600">
      Enter a GitHub repository URL and index it to get started.
    </p>
  )}
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={
                message.role === "user"
                  ? "flex justify-end"
                  : "flex justify-start"
              }
            >
              <div
                className={
                  message.role === "user"
                    ? "max-w-3xl rounded-2xl rounded-br-md bg-white px-4 py-3 text-sm leading-6 text-black"
                    : "max-w-3xl rounded-2xl rounded-bl-md border border-white/10 bg-white/[0.04] px-4 py-3 text-sm leading-6 text-zinc-200"
                }
              >
                <div className="whitespace-pre-wrap">
                  {message.content}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-bl-md border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-zinc-400">
                {mode === "document_qa"
                  ? "Nexkora is reading the document..."
                  : mode === "github_qa"
                  ? "Nexkora is analyzing the GitHub repository..."
                  : "Nexkora is analyzing your code..."}
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="border-t border-white/10 bg-black/20 px-4 py-4">
        <form
          onSubmit={handleSubmit}
          className="mx-auto max-w-5xl"
        >
          <div className="overflow-hidden rounded-2xl border border-white/10 bg-zinc-950">
            <textarea
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              placeholder={
                placeholderByMode[mode]
              }
              autoFocus
              spellCheck={false}
              rows={8}
              maxLength={12000}
              disabled={
                isLoading ||
                isUploading
              }
              className="w-full resize-none bg-transparent px-4 py-4 text-sm leading-6 text-white outline-none placeholder:text-zinc-600 disabled:cursor-not-allowed"
            />

            <div className="flex items-center justify-between border-t border-white/10 px-3 py-3">
              <span className="text-xs text-zinc-600">
                {input.length}/12000
              </span>

              <button
                type="submit"
                disabled={
                  isLoading ||
                  isUploading ||
                  isIndexingGithub ||
                  input.trim().length === 0 ||
                  (mode === "document_qa" &&
                    !documentId) ||
                  (mode === "github_qa" && !githubIndexed)
                }
                className="rounded-lg bg-white px-4 py-2 text-sm font-medium text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {isLoading
                  ? "Working..."
                  : buttonLabelByMode[mode]}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}