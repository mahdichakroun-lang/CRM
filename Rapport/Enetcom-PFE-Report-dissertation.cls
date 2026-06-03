\usepackage{silence}
\WarningsOff*
\LoadClassWithOptions{report}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Packages to use
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\usepackage[a4paper,left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm]{geometry}
\usepackage{environ}
\usepackage{verse}
\usepackage[table]{xcolor}
\usepackage[explicit]{titlesec}
\usepackage{chngcntr}
\usepackage{fancyhdr}
\usepackage{caption}
\usepackage{subcaption}
\usepackage[hidelinks]{hyperref}
\usepackage{needspace}
\usepackage{pdfpages}
\usepackage{chngcntr}
\usepackage{enumitem}
\usepackage[bottom]{footmisc}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% LANGUE FRANÇAISE AVEC CÉSURE - ESSENTIEL POUR JUSTIFICATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\usepackage[french]{babel}

\usepackage{varioref}
\usepackage{acronym}
\usepackage{minitoc}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Include required packages
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[skins]{tcolorbox}
\usepackage{varioref}
\usepackage[export]{adjustbox}
\usepackage{setspace}
\usepackage{listings}
\usepackage{color}
\usepackage{tabularx}
\usepackage{ctable}
\usepackage{graphicx}
\usepackage{multirow}
\usepackage{tikz}
\usepackage{seqsplit}
\usepackage{fontenc}
\usepackage{wrapfig}
\usepackage{setspace}
\usepackage[all]{nowidow}
\usepackage{acronym}
\usepackage{array}
% SUPPRIMÉ: ragged2e car il peut interférer avec la justification
\usepackage{enumitem}
\usepackage{xcolor}
\definecolor{Gris1}{RGB}{116,134,170}
\definecolor{Gris2}{RGB}{249,249,249}
\usepackage[titletoc,title]{appendix}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MICRO-TYPOGRAPHIE POUR MEILLEURE JUSTIFICATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\usepackage{microtype}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Include probable needed packages
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\usepackage{siunitx} \sisetup{mode=math, range-phrase=--, range-units=single}
\DeclareSIUnit{\rms}{\ped{RMS}}
\DeclareSIUnit[quantity-product = ]\percent{\char`\%}
\DeclareUnicodeCharacter{2212}{\textendash}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\def\defaultFont{ptm}
\renewcommand*{\familydefault}{\defaultFont}
\renewcommand\UrlFont{\ignore{Actually do nothing!}}

\definecolor{tableRow1}{RGB}{210,234,241}
\definecolor{gray75}{gray}{0.75}
\definecolor{reportType}{HTML}{013873}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Define styles
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 \newlength\BoxWd
 \setlength\BoxWd{10mm}
 \newlength\Aux
  % chapter tiltes formatting
  \titleformat{\chapter}[display]%
    {\fontsize{21}{6}\bfseries\selectfont%
      \settowidth\Aux{\textcolor{white}{\Huge\thechapter}}%
      \ifnum\Aux>\BoxWd%
        \setlength\BoxWd{\Aux}%
      \else\fi%
    }%
    {%
      {\hspace*{-1.5mm}\normalfont\fontsize{14}{6}\selectfont{Chapitre}}\\%
      \colorbox{black}{%
        \parbox[c][20mm][t]{\BoxWd}{%
          \vspace{2.5mm}\centering\textcolor{white}{\Huge\thechapter}%
        }%
      }%
    }%
    {-10mm}%
    {%
      \vspace{-5mm}\hspace*{15mm}\titlerule\\\\\hspace*{15mm}#1%
    }
  % chapter tiltes formatting (numberless)
  \titleformat{name=\chapter, numberless}[display]%
    {\fontsize{26}{6}\bfseries\selectfont%
      \settowidth\Aux{\textcolor{white}{\Huge\thechapter}}%
      \ifnum\Aux>\BoxWd%
        \setlength\BoxWd{\Aux}%
      \else\fi%
    }%
    {%
      {\hspace*{-1.5mm}\normalfont\fontsize{14}{6}\selectfont{~}}\\%
      \colorbox{black}{%
        \parbox[c][20mm][t]{\BoxWd}{%
          \vspace{2.5mm}\centering\textcolor{white}{~}%
        }%
      }%
    }%
    {-10mm}%
    {%
      \vspace{-5mm}\hspace*{15mm}\titlerule\\\\\hspace*{15mm}#1%
    }
% chapter tiltes spacing
\titlespacing*{\chapter}{0pt}{0pt}{50pt}
\titleformat{\section}[block]%
  {\Large\bfseries}{\thesection}%
  {10pt}{\Large{\bfseries{#1}}}
\titleformat{\paragraph}[block]%
  {\normalfont\normalsize\bfseries}%
  {\theparagraph}{1em}{#1}

% MODIFIÉ: justification centrée au lieu de RaggedRight
\captionsetup{labelfont=bf,font={singlespacing},font=small,textfont=sc,textfont=bf}

%%%%%%%%%%%% My style begin %%%%%%%%%%%%
\fancypagestyle{MyStyle}{
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0.5pt}
  \fancyhead[L]{}
  \fancyfoot[R]{\fontsize{12}{12}\selectfont Page \thepage}
  \fancyfoot[L]{\fontsize{12}{12}\selectfont IPSAS}
}
\renewcommand{\chaptermark}[1]{\markboth{\MakeUppercase{#1}}{}}
%%%%%%%%%%%% My style end %%%%%%%%%%%%
\fancypagestyle{plain}{
  \fancyhf{}
  \renewcommand{\headrulewidth}{0.5pt}
  \renewcommand{\footrulewidth}{0.5pt}
  \fancyhead[L]{\fontsize{12}{12}\selectfont\textsc{\MakeLowercase{\leftmark}}}
  \fancyfoot[R]{\fontsize{12}{12}\selectfont Page \thepage}
  \fancyfoot[L]{\fontsize{12}{12}\selectfont\ IPSAS}
}
\setlength{\fboxsep}{0mm}%
\setlength{\fboxrule}{1pt}%
\counterwithout{footnote}{chapter}
\pagestyle{plain}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Useful commands
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand{\ignore}[2]{\hspace{0mm}#2}
\newcommand{\HRule}[1][\linewidth]{%
  \rule{#1}{0.5mm}%
}
\newcommand{\printBigName}{%
  \leavevmode\color{titleColorGray}\setmainfont{Cambria}\fontsize{23pt}{23pt}\selectfont\textbf{\@name}
}
\newcommand{\putPhoto}[1] {%
  \includegraphics[width=35mm, height=35mm]{#1}
}
\newcommand{\highlight}[1] {%
  \textit{#1}%
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Init commands
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\setcounter{secnumdepth}{5}
\setcounter{tocdepth}{3}
\renewcommand\theparagraph{\alph{paragraph})}
\renewcommand\thesubparagraph{\roman{subparagraph}.}
\setlength{\parskip}{1ex}
\setlist[enumerate]{itemsep=-0.35\baselineskip}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PARAMÈTRES DE JUSTIFICATION - C'EST ICI LA CLÉ !
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% AVANT: hyphenpenalty=10000 (BLOQUAIT la césure)
% MAINTENANT: Valeurs qui PERMETTENT la justification

\hyphenpenalty=50
\exhyphenpenalty=50
\doublehyphendemerits=10000
\finalhyphendemerits=5000
\tolerance=1000
\emergencystretch=3em
\hbadness=10000
\vbadness=10000
\hfuzz=50pt

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% New Environments
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\NewEnviron{pfe-enetcom} {%
  \begingroup%
  \BODY%
  \endgroup%
}%