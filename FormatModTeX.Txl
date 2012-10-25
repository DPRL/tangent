include "Grammars/BST_mod.Grammar"
include "Grammars/Symbol_Classes.Grammar"

% Overrides grammar definition (simplification)
redefine symbol
		[symbol_id_attributes]
	|	':: 'FN [texCommand]
	|	[tex2html_comment_mark]
end redefine

redefine symbol_node
		...
	|	'{ [spatial_relation] [baselineStructureTree] '}
end redefine

rule filterTex2HtmlComments
	replace [repeat symbol_node]
		S[symbol_node] R[repeat symbol_node]
		
	deconstruct S
		_[tex2html_comment_mark]

	by
		R
end rule

rule replaceIsymbol
	replace $ [isymbol]
		S[symbol]

	construct label[number]
		1

	by
		':: 'ARG label S '::
end rule

rule labelRelations
	replace $ [spatial_relation]
		R[relation_type]

	by
		':: 'REL R
end rule

rule replaceAllTexFns
	replace $ [symbol_node]
		S[symbol] Rel1[relation_node] R[repeat relation_node]
		
	deconstruct * [texCommand] S
		T[texCommand]

	% To be an argument, there must be no spatial relationship.
	deconstruct Rel1
		'{ B[baselineStructureTree] '}

	construct NewRel1[repeat relation_node]
		Rel1

	by
		':: 'FN T  NewRel1[. R]
end rule	

% This is a bit redundant given the function above.
rule rewriteTexFnNodes
	replace $ [symbol_node]
		':: 'FN T[texCommand] R[repeat relation_node]

	construct relations[number]
		_[length R]

	construct Args[number]
		_[countFunctionArgs R]

	where 
		relations[> 0]
	by
		':: 'FN T R[labelRelArgs Args] 

end rule


function replaceTex
	replace [symbol]
		S[symbol]
		
	deconstruct * [texCommand] S
		T[texCommand]

	by
		':: 'FN T 
end function

% RZ: Debug: count only arguments for functions, which (ASSUMPTION)
%     should precede spatial relationship operators (_,^).
function countFunctionArgs R[repeat relation_node]
	replace [number]
		N[number]

	deconstruct R
		Next[relation_node] Rest[repeat relation_node]

	deconstruct Next
		'{ _[baselineStructureTree] '}

	by
		N[+1][countFunctionArgs Rest]
end function


rule rewriteNode
	replace $ [symbol_node]
		S[symbol] R[repeat relation_node]

	construct relations[number]
		_[length R]

	construct Args[number]
		_[countFunctionArgs R]

	where 
		relations[> 0]
	by
		S R[labelRelArgs Args] 
end rule


function replaceIfNegative N[number]
	replace [number]
		K[number]
	
	where 
		K[< N]
	
	by
		N
end function



function applyRelationLabel ArgNum[number]
	replace [relation_node]
		S[spatial_relation] '{  BST[baselineStructureTree] '}

	construct Numbering[number]
		ArgNum[replaceIfNegative 1]

	by
		 S ':: 'ARG Numbering BST '::
end function

function applyFunctionLabel ArgNum[number]
	replace [relation_node]
		'{  BST[baselineStructureTree] '}

	construct Numbering[number]
		ArgNum[replaceIfNegative 1]

	by
		 ':: 'ARG ArgNum BST '::
end function

function labelSymbolRelArgs S[symbol] ArgNum[number]
	% DEBUG: only create arguments for LaTeX commands.
	deconstruct * [texCommand] S
		t[texCommand]

	replace [repeat relation_node]	
		R[repeat relation_node]
	by
		R[labelRelArgs ArgNum]
end function


function labelRelArgs ArgNum[number]
	replace [repeat relation_node]
		R[relation_node] Rest[repeat relation_node]

	construct NextNum[number]
		ArgNum[- 1]

	by
		R[applyRelationLabel ArgNum] 
		 [applyFunctionLabel ArgNum]
		
		Rest[labelRelArgs NextNum]
end function

rule removeRedundantBraces
	replace [symbol_node]
		'{ '{ B[baselineStructureTree] '} '} Rel[repeat relation_node]
	
	by
		'{ B '} Rel
end rule


% **Careful; assumes symbols only as arguments in REL nodes.
function addNodes R[relation_node]
	replace [repeat symbol_node]
		S[repeat symbol_node]

	deconstruct R
		'{ Symbols[repeat symbol_node] '}

	by
		S[. Symbols]
end function

function attachRelationsToLastSymbol Rels[repeat relation_node]
	replace * [repeat symbol_node]
		S[symbol] R[repeat relation_node]

	by
		S R[. Rels]
end function

% Designed to remove braces for adjacent expressions.
rule removeUnneededBraces
	replace [repeat symbol_node]
		B[symbol] '{ Nested[repeat symbol_node] '} Rels[repeat relation_node] 
		Rest[repeat symbol_node]

	deconstruct not * [texCommand] B
		t[texCommand] 

	construct NestedNodes[repeat symbol_node]
		_[addNodes each Rels]

	construct FirstNode[repeat symbol_node]
		B

	construct NewSymbols[repeat symbol_node]
		FirstNode[. Nested][addNestedBST each Rels] 

		% DEBUG: if first relation is not nested, none are (safe assumption?)
		%[attachRelationsToLastSymbol Rels]

	by
		NewSymbols[. Rest]
end rule

rule removeUnneededBraces2
	replace [repeat symbol_node]
		'{ B[symbol] '} '{ Nested[repeat symbol_node] '} Rels[repeat relation_node] 
		Rest[repeat symbol_node]

	deconstruct not * [texCommand] B
		t[texCommand] 

	construct NestedNodes[repeat symbol_node]
		_[addNodes each Rels]

	construct FirstNode[repeat symbol_node]
		B

	construct NewSymbols[repeat symbol_node]
		FirstNode[. Nested][addNestedBST each Rels]

		% DEBUG: if first relation is not nested, none are (safe assumption?)
		%[attachRelationsToLastSymbol Rels]

	by
		NewSymbols[. Rest]
end rule

function attachRel Relations[repeat relation_node] Remaining[number]
	where 
		Remaining[= 0]

	replace [symbol_node]
		S[symbol] R[repeat relation_node]

	by
		S R[. Relations]
end function

function attachRelationsAtEnd Relations[repeat relation_node]
	replace * [repeat symbol_node]
		Symbol[symbol_node] 
		Next[repeat symbol_node]

	construct Length[number]
		_[length Next]

	by
		Symbol[attachRel Relations Length]  
		Next[attachRelationsAtEnd Relations]
end function

% Note: this associates spatial relationships with the *last* symbol
%      of the nested expression.
rule unbraceSymbolNodes
	replace [repeat symbol_node]
		'{ B[baselineStructureTree]'} Rel[repeat relation_node] R[repeat symbol_node]

	deconstruct B
		Slist[repeat symbol_node]

	construct NewSymbols[repeat symbol_node]
		Slist[attachRelationsAtEnd Rel]

	by
		NewSymbols[. R]
end rule


function addNestedBST R[relation_node]
	replace [repeat symbol_node]
		S[repeat symbol_node]

	deconstruct R
		'{ BST[baselineStructureTree] '}

	construct SNew[symbol_node]
		'{ BST '}

	by
		S[. SNew]
end function

% Simply remove all begin and end directives, along with whatever environment they
% identify.
rule removeBeginEnd
	replace [repeat symbol_node]
		S[symbol] '{ R[repeat symbol_node] '} Rest[repeat symbol_node]

	construct FilterList[repeat symbol]
		'\begin '\end

	where
		S[= each FilterList]

	by
	    % DEBUG
		%R[. Rest]
		Rest
end rule

rule filterFns
	replace [repeat symbol_node]
		S[symbol] R[repeat relation_node] Rest[repeat symbol_node]

	construct FilterList[repeat symbol]
		'\displaystyle '\displaymath '\begin '\end '\eqno '\mbox
		'\left '\right
	
	where
		S[= each FilterList]
	
	by
		_[addNestedBST each R][. Rest]
end rule

rule rewriteNestedRelationships
	replace [repeat symbol_node]
		S1[symbol] R1[repeat relation_node] '{ R[spatial_relation] B[baselineStructureTree] '} 
		Rest[repeat symbol_node]

	construct NewRelNode[relation_node]
		R '{ B '}

	construct NewSymbolNode[symbol_node]
		S1 R1[. NewRelNode]

	by
		_[. NewSymbolNode][. Rest] 
end rule


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Dealing with nested adjacent
% symbols.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function hasBracketedNestedRegion
	match * [relation_node]
		'{ _[baselineStructureTree] '}
end function

% Note that relations must appear outside bracketed region, according to the
% grammar definition.
function hasNestedSymbols
	match [repeat relation_node]
		R[spatial_relation]'{ B[baselineStructureTree] '} Rest[repeat relation_node]

	where
		Rest[hasBracketedNestedRegion]
end function

function findRealRelIndex Rels[repeat relation_node]
	replace [number]
		N[number]

	construct Length[number]
		_[length Rels]

	where 
		N[<= Length]

	construct NewList[repeat relation_node]
		Rels[select N N]

	where not
		NewList[hasBracketedNestedRegion]
	
	construct NewCount[number]
		N[+ 1]

	by
		NewCount[findRealRelIndex Rels]
end function

rule liftNestedAdjacentSymbols
	replace [repeat symbol_node]
		S[symbol] Rels[repeat relation_node]
		Rest[repeat symbol_node]

	% If this is a function, stop.
	deconstruct not * [symbol] S
		':: 'FN t[texCommand]

	where
		Rels[hasNestedSymbols]

	% Assume that relationships for this symbol must appear in the intial
	% 'relation_nodes' with which it is associated.
	construct InitialRealRels[number]
		2
		
	construct FinalIndex[number]
		InitialRealRels[findRealRelIndex Rels]

	construct Length[number]
		_[length Rels]

	% Index will be > list length if all relations are proper.
	where not
		FinalIndex[> Length]

	construct LastValidRelIndex[number]
		FinalIndex[- 1]

	construct ValidRels[repeat relation_node]
		Rels[select 1 LastValidRelIndex]

	construct NestedRegions[repeat relation_node]
		Rels[select FinalIndex Length]

	construct NewNode[symbol_node]
		S ValidRels

	by
		_[. NewNode][addNestedBST each NestedRegions][. Rest]
end rule

function main
	replace [program]
		P[program]
	by
		P
		 % Filter tokens, identify functions, 
		 % Map functions, BEFORE handling relationships.
		 [removeBeginEnd]
		 [filterTex2HtmlComments]
		 [filterFns]
		 [replaceAllTexFns]
		 [rewriteTexFnNodes]

		 % Handle nested relationships, and 'lift' adjacent expressions
		 % parsed as relation_nodes to symbol_nodes.
		 [rewriteNestedRelationships]
		 [liftNestedAdjacentSymbols]

		 % Normalize bracketing/bracing.
		 [removeRedundantBraces]
		 [removeUnneededBraces] 
		 [removeUnneededBraces2] 
		 [unbraceSymbolNodes]

		 % Map relations.
		 [rewriteNode]
		 [labelRelations]
		 [replaceIsymbol]
end function

