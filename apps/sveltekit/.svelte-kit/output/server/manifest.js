export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set([]),
	mimeTypes: {},
	_: {
		client: {start:"_app/immutable/entry/start.BSS9603T.js",app:"_app/immutable/entry/app.Cp4wN_qq.js",imports:["_app/immutable/entry/start.BSS9603T.js","_app/immutable/chunks/CVCu0SHQ.js","_app/immutable/chunks/fZzhJA23.js","_app/immutable/chunks/DEwDV0-h.js","_app/immutable/entry/app.Cp4wN_qq.js","_app/immutable/chunks/DEwDV0-h.js","_app/immutable/chunks/fZzhJA23.js","_app/immutable/chunks/Bzak7iHL.js","_app/immutable/chunks/D4fUw0xg.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
