// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require("vscode");
const axios = require("axios");

const BE_SERVICE_HOST = "localhost";
const BE_SERVICE_PORT = 5000;
const BE_SERVICE_ENDPOINT = "generate_docs";

const LANGUAGES_SUPPORT = ["python", "javascript"];

function getHighlightedText(editor) {
  const { selection } = editor;
  const highlightRange = new vscode.Range(
    editor.selection.start,
    editor.selection.end
  );
  const highlighted = editor.document.getText(highlightRange);
  return { selection, highlighted };
}

function getWidth(offset) {
  const rulers = vscode.workspace.getConfiguration("editor").get("rulers");
  const maxWidth = rulers != null && rulers.length > 0 ? rulers[0] : 100;
  const width = maxWidth - offset;
  return width;
}

function activate(context) {
  const write = vscode.commands.registerCommand("docs.write", async () => {
    const editor = vscode.window.activeTextEditor;
    if (editor == null) {
      return;
    }

    const { languageId, getText, fileName } = editor.document;

    const { selection, highlighted } = getHighlightedText(editor);
    let location = null;
    let line = null;

    if (!highlighted) {
      let document = editor.document;
      let curPos = editor.selection.active;
      location = document.offsetAt(curPos);
      line = document.lineAt(curPos);
      if (line.isEmptyOrWhitespace) {
        vscode.window.showErrorMessage(
          `Please select a line with code and try again.`
        );
        return;
      }
      if (!LANGUAGES_SUPPORT.includes(languageId)) {
        vscode.window.showErrorMessage(`Please select code and try again..`);
        return;
      }
    }

    vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "Generating documentation",
      },
      async () => {
        const docsPromise = new Promise(async (resolve, _) => {
          console.log(highlighted);
          try {
            const WRITE_ENDPOINT = `http://${BE_SERVICE_HOST}:${BE_SERVICE_PORT}/${BE_SERVICE_ENDPOINT}`; //"http://localhost:8000/get_new_text";
            console.log(WRITE_ENDPOINT)
            const {
              data: { docstring, position },
            } = await axios.post(WRITE_ENDPOINT, {
              languageId: languageId,
              commented: true,
              source: "vscode",
              context: getText(),
              width: line
                ? getWidth(line.firstNonWhitespaceCharacterIndex)
                : getWidth(selection.start.character),
              code: highlighted,
              location: location,
              line: line?.text,
            });
            vscode.commands.executeCommand("docs.insert", {
              position: position,
              content: docstring,
              selection: selection,
            });
            resolve("Completed generating");
          } catch (err) {
            resolve("Error");
            const errMessage = err?.response?.data?.error;
            if (errMessage != null) {
              vscode.window.showErrorMessage(errMessage);
            } else {
              vscode.window.showErrorMessage(
                "Error occurred while generating docs"
              );
            }
          }
        });

        await docsPromise;
      }
    );
  });

  const insert = vscode.commands.registerCommand(
    "docs.insert",
    async ({ position, content, selection }) => {
      const editor = vscode.window.activeTextEditor;
      if (editor == null) {
        return;
      }
      if (position === "below") {
        const start = selection.start.line;
        const startLine = editor.document.lineAt(start);

        const tabbedDocstring = content
          .split("\n")
          .map((line) => `\t${line}`)
          .join("\n");
        const snippet = new vscode.SnippetString(`\n${tabbedDocstring}`);
        editor.insertSnippet(snippet, startLine.range.end);
      } else if (position === "above") {
        const snippet = new vscode.SnippetString(`${content}\n`);
        let position;
        if (
          selection.start.line == selection.end.line &&
          selection.start.character == selection.end.character
        ) {
          let document = editor.document;
          const curPos = editor.selection.active;
          const desiredLine = document.lineAt(curPos);
          const lineNum = desiredLine.range.start.line;
          position = new vscode.Position(
            lineNum,
            desiredLine.firstNonWhitespaceCharacterIndex
          );
        } else {
          position = selection.start;
        }
        editor.insertSnippet(snippet, position);
      }
    }
  );
  context.subscriptions.push(write, insert);
}

// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
