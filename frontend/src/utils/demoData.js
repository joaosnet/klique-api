export const DEMO_CARDS = [
    {
        id: 'demo-1',
        template_type: 'if_then',
        probability_heat_score: 72,
        scenario_context:
            'Você está a negociar um aumento salarial. O teu gestor diz que o orçamento para aumentos está "congelado este trimestre", mas você sabe que um colega acabou de ser promovido.',
        question:
            'Se o gestor usa a restrição de "budget congelado", qual é a jogada dominante que maximiza o teu payoff sem queimar a relação?',
        predicted_outcome:
            'O "budget congelado" é uma âncora de negociação, não uma restrição real. Aceitar silenciosamente sinaliza que este frame funcionou e será repetido.',
        game_theory_explanation:
            'Este é um Jogo de Barganha com Assimetria de Informação. O gestor tem incentivo em minimizar o custo salarial. A estratégia dominante é converter o jogo de 1 rodada para multi-rodada: "Entendo o constrangimento de agora. Posso propor definirmos métricas concretas para revisitar isto em Janeiro?" Isto preserva a relação, sinaliza valor e cria um compromisso público do gestor.',
    },
    {
        id: 'demo-2',
        template_type: 'black_swan',
        probability_heat_score: 88,
        scenario_context:
            'Combinaste um jantar com alguém que conheceste online. 20 minutos antes do encontro, ela cancela com "surgiu uma emergência de trabalho". Três horas depois envia uma selfie num bar com amigos.',
        question:
            'Como interpretas este sinal pela lente da Teoria dos Jogos, e qual é o próximo movimento que melhor preserva o teu Status Signal?',
        predicted_outcome:
            'O sinal indica teste de reacção ou baixo custo percebido da tua presença. Reagir imediatamente confirma alto investimento emocional e reduz o teu poder de barganha.',
        game_theory_explanation:
            'Em jogos de atracção, o valor percebido (Status Signal) é inversamente proporcional à disponibilidade aparente. O cancelamento foi um teste de Costly Signal — a selfie foi a verificação. A jogada ótima: não reages por 24–48h. Depois reinicias com um frame diferente de alto status: "Vi algo que acho que ia interessar-te — [referência específica ao que ela gosta]." Isto reposiciona-te como o agente de iniciativa, não o receptor.',
    },
    {
        id: 'demo-3',
        template_type: 'payoff_matrix',
        probability_heat_score: 61,
        scenario_context:
            'O teu colega apresentou o trabalho que desenvolvestes juntos numa reunião com a direção, sem te mencionar. O teu gestor elogiou o colega publicamente.',
        question:
            'Cooperas em silêncio, confrontas o colega em privado, ou clarificas a tua contribuição ao gestor? Qual estratégia maximiza o teu payoff a longo prazo?',
        predicted_outcome:
            'Silêncio cria precedente que o comportamento tem custo zero. Confronto directo tem risco de parecer mesquinho. A jogada ótima é reframing de contribuição com o gestor num contexto natural.',
        game_theory_explanation:
            'Este é um Dilema do Prisioneiro assimétrico com elemento de Reputação. Cooperação silenciosa é dominada — cria incentivo para o colega repetir. Confronto directo tem alto risco de reputação negativa. A estratégia ótima: "Fico contente que a análise que o X e eu trabalhámos sobre [tema] tenha ressoado — temos mais dados se quiserem aprofundar." Clarifica a tua contribuição, posiciona-te como colaborador valioso e não como queixoso.',
    },
];

export const DEMO_DOMAINS = [
    {
        domain: { id: 'demo-domain-1', name: 'Dinâmicas de Escritório', theme: 'office' },
        stats: { cards_count: 14, due_today: 3, accuracy: 0.82 }
    },
    {
        domain: { id: 'demo-domain-2', name: 'Negociação Salarial', theme: 'finance' },
        stats: { cards_count: 8, due_today: 0, accuracy: 0.95 }
    },
    {
        domain: { id: 'demo-domain-3', name: 'Atracção e Status', theme: 'dating' },
        stats: { cards_count: 22, due_today: 5, accuracy: 0.64 }
    }
];
