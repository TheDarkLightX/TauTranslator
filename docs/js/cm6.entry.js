import {EditorView, keymap, drawSelection, highlightActiveLine} from '@codemirror/view';
import {EditorState} from '@codemirror/state';
import {defaultHighlightStyle, syntaxHighlighting} from '@codemirror/language';
import {defaultKeymap, history, historyKeymap} from '@codemirror/commands';
import {autocompletion} from '@codemirror/autocomplete';

window.CM6 = { EditorView, EditorState, drawSelection, highlightActiveLine, defaultHighlightStyle, syntaxHighlighting, keymap, defaultKeymap, history, historyKeymap, autocompletion };
