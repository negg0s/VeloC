/**
 * VeloC VS Code Extension Entrypoint
 * Spawns the VeloC LSP Server (`veloc lsp`) and coordinates language features.
 */

const vscode = require('vscode');
const { LanguageClient, TransportKind } = require('vscode-languageclient/node');
const path = require('path');

let client;

function activate(context) {
    console.log('[VeloC] Language Extension activating...');

    // Server options: launch veloc lsp
    const serverOptions = {
        command: 'veloc',
        args: ['lsp'],
        transport: TransportKind.stdio
    };

    // Client options
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'veloc' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.vc')
        }
    };

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('veloc.run', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const term = vscode.window.createTerminal('VeloC Run');
                term.show();
                term.sendText(`veloc run "${editor.document.fileName}"`);
            }
        }),
        vscode.commands.registerCommand('veloc.test', () => {
            const term = vscode.window.createTerminal('VeloC Test');
            term.show();
            term.sendText('veloc test');
        }),
        vscode.commands.registerCommand('veloc.format', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const term = vscode.window.createTerminal('VeloC Format');
                term.sendText(`veloc fmt "${editor.document.fileName}"`);
            }
        })
    );

    try {
        client = new LanguageClient(
            'velocLanguageServer',
            'VeloC Language Server',
            serverOptions,
            clientOptions
        );
        client.start();
        console.log('[VeloC] Language Server started successfully.');
    } catch (err) {
        console.log('[VeloC] LSP Client notice:', err.message);
    }
}

function deactivate() {
    if (!client) return undefined;
    return client.stop();
}

module.exports = {
    activate,
    deactivate
};
