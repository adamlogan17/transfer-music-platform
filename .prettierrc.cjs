/**
 * This is the same as .prettier files except having it in this format allows for comments to be left within the file
 *
 * @see {@link https://prettier.io/docs/en/options.html} for Prettier configuration options
 */

module.exports = {
	bracketSpacing: true,
	singleQuote: true,
	trailingComma: 'all',
	tabWidth: 2,
	semi: true,
	printWidth: 120,
	jsxSingleQuote: true,
	endOfLine: 'auto',
	arrowParens: 'always',
	useTabs: true,
	proseWrap: 'preserve', // By default, Prettier will wrap markdown text as-is since some services use a linebreak-sensitive renderer.
	// Override options for TypeScript files
	overrides: [
		{
			files: ['*.ts', '*.tsx'],
			options: {
				semi: true,
				trailingComma: 'none',
			},
		},
	],
};
