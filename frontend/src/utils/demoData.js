export const DEMO_CARDS = [
    {
        id: 'demo-1',
        card_format: 'concurso_certo_errado',
        template_type: 'if_then',
        probability_heat_score: 95,
        scenario_context: 'Direito Administrativo - Atos Administrativos',
        question: 'A presunção de legitimidade dos atos administrativos é absoluta, o que impede que o particular produza prova em contrário até que haja decisão judicial transitada em julgado.',
        predicted_outcome: 'Errado',
        correct_answer: 'Errado',
        explanation: 'A presunção de legitimidade e veracidade dos atos administrativos é RELATIVA (juris tantum). Ela admite prova em contrário pelo particular, que tem o ônus de provar eventual vício no ato.',
        media_urls: [],
    },
    {
        id: 'demo-2',
        card_format: 'concurso_multipla_escolha',
        template_type: 'payoff_matrix',
        probability_heat_score: 88,
        scenario_context: 'Direito Constitucional - Direitos Fundamentais',
        question: 'Sobre o direito de propriedade garantido na Constituição Federal de 1988, é correto afirmar:',
        options: [
            'A propriedade atenderá a sua função social, exceto a propriedade rural produtiva.',
            'No caso de perigo público iminente, a autoridade competente não poderá usar de propriedade particular sem autorização judicial prévia.',
            'A lei estabelecerá o procedimento para desapropriação por necessidade ou utilidade pública, mediante justa e prévia indenização em dinheiro.',
            'A sucessão de bens de estrangeiros situados no País será sempre regulada pela lei brasileira em benefício do cônjuge brasileiro.',
            'A pequena propriedade rural, mesmo que não trabalhada pela família, é impenhorável para pagamento de débitos.'
        ],
        predicted_outcome: 'A lei estabelece o procedimento para desapropriação por necessidade ou utilidade pública, mediante justa e prévia indenização em dinheiro.',
        correct_answer: 'A lei estabelecerá o procedimento para desapropriação por necessidade ou utilidade pública, mediante justa e prévia indenização em dinheiro.',
        explanation: 'A alternativa correta é a C (Art. 5º, XXIV da CF/88). Exceções à indenização prévia e em dinheiro incluem a desapropriação-sanção urbana (títulos da dívida pública) e rural (títulos da dívida agrária).',
        media_urls: [],
    },
    {
        id: 'demo-3',
        card_format: 'flashcard_basico',
        template_type: 'black_swan',
        probability_heat_score: 50,
        scenario_context: 'Língua Portuguesa - Crase',
        question: 'Quais são as três palavras essenciais em que a crase NUNCA ocorre antes?',
        predicted_outcome: 'Verbos, palavras masculinas e pronomes de tratamento',
        correct_answer: 'Verbos, palavras masculinas e pronomes de tratamento (na maioria dos casos)',
        explanation: 'Dica: "Crase antes de verbo é tiro no nervo!"',
        media_urls: [],
    },
    {
        id: 'demo-4',
        card_format: 'game_theory',
        template_type: 'black_swan',
        probability_heat_score: 88,
        scenario_context: 'Combinaste um jantar com alguém que conheceste online. 20 minutos antes do encontro, ela cancela com "surgiu uma emergência de trabalho".',
        question: 'Como interpretas este sinal pela lente da Teoria dos Jogos, e qual é o próximo movimento?',
        predicted_outcome: 'O sinal indica teste de reacção ou baixo custo percebido da tua presença.',
        game_theory_explanation: 'Em jogos de atracção, o valor percebido é inversamente proporcional à disponibilidade aparente...',
        media_urls: [],
    },
];

export const DEMO_DOMAINS = [
    {
        domain: { id: 'demo-domain-1', name: 'Direito Constitucional', theme: 'office' },
        stats: { cards_count: 140, due_today: 32, accuracy: 0.82 }
    },
    {
        domain: { id: 'demo-domain-2', name: 'Língua Portuguesa', theme: 'finance' },
        stats: { cards_count: 85, due_today: 10, accuracy: 0.95 }
    },
    {
        domain: { id: 'demo-domain-3', name: 'Dinâmicas de Escritório', theme: 'dating' },
        stats: { cards_count: 22, due_today: 5, accuracy: 0.64 }
    }
];
