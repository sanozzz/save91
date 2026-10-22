/**
 * Janta deposit agent interview. One phone call, about 40 taps.
 * You tap on the agent's behalf while the agent talks. The agent is not being hired today.
 *
 * Three goals:
 *   1. Could we hire agents like this as our street fleet, instead of building one?
 *   2. Who is the agent?
 *   3. Who are the agent's customers?
 *
 * Read the question only, never the choices. Tap the nearest band.
 * Other = an exact number or a name. Ask what happened, never "would you".
 * Never say a company name, an app name, or a market-size number.
 * No customer names or phones. Rs 300 is thanks, at the end only.
 *
 * Run: script.google.com > blank project > paste > run createJantaDepositInterview.
 * Each run makes a new form and sheet. Older forms do not update.
 */
function createJantaDepositInterview() {
  const form = FormApp.create('Janta deposit — could these agents be our fleet?');
  form.setDescription(
    'Read the question. Tap what is said. Never read the choices. Other = an exact number or a name.\n\n' +
    'Say this, then stop talking:\n' +
    '"Main aapka kaam aur aapke customers ko samajhna chahta hoon. ' +
    'Main naukri nahi de raha. Koi bhi sawaal chhod sakte ho."'
  );
  form.setProgressBar(true);
  form.setAllowResponseEdits(true);
  form.setConfirmationMessage('Saved. Use the edit link if the call continues. No customer names.');
  if (typeof form.setPublished === 'function') form.setPublished(true); // newer Forms start unpublished

  // Alone on page 1, so "No" can submit without the required fields below.
  const consent = form.addMultipleChoiceItem()
    .setTitle('Main sirf apne liye notes le raha hoon. Kisi customer ka naam ya phone nahi likhunga. Theek hai?')
    .setHelpText('Stop if the answer is no.')
    .setRequired(true);
  consent.setChoices([
    consent.createChoice('Yes', FormApp.PageNavigationType.CONTINUE),
    consent.createChoice('No. Stop.', FormApp.PageNavigationType.SUBMIT),
  ]);

  addSection(form, '1. The agent', 'Goal 2: who the agent is. Name, city and area are typed.');
  form.addDateItem().setTitle('Date of the call');
  addText(form, 'Aapka naam kya hai?').setRequired(true);
  addText(form, 'Aap kis sheher mein kaam karte ho?').setRequired(true);
  addText(form, 'Aap kaun sa ilaaka cover karte ho?', 'Neighbourhood or route.');
  addChoice(form, 'Aap yeh kaam kitne saal se kar rahe ho?',
    ['Under 1 year', '1 to 3 years', '3 to 10 years', 'Over 10 years']);
  addChoice(form, 'Yeh kaam aapko kaise mila?',
    ['A family member did it', 'Through an agent or a friend', 'The bank or society hired directly', 'Took over a book']);
  addChoice(form, 'Aap kitni jagah se jude ho?',
    ['One bank', 'One society', 'More than one', 'Works independently']);
  addChoice(form, 'Aapki umar kitni hai?',
    ['Under 25', '25 to 35', '35 to 45', '45 to 55', 'Over 55']);
  addChoice(form, 'Aapne kahan tak padhai ki hai?',
    ['Below 10th', '10th', '12th', 'Graduate', 'More than graduate']);
  addChoice(form, 'Roz round mein kitne ghante lagte hain?',
    ['Under 3 hours', '3 to 5 hours', '5 to 8 hours', 'More than 8 hours']);
  addChecks(form, 'Round ke baad din mein kya karte ho?',
    ['Another job', 'Own shop or business', 'Sells insurance or loans', 'Home and family', 'Nothing fixed'],
    'Tick everything said.');
  addChecks(form, 'Phone par aap kya-kya karte ho?',
    ['Calls only', 'WhatsApp', 'UPI payments', 'Videos', 'A work app', 'No smartphone'],
    'Tick everything said.');

  addSection(form, '2. The book', 'Goals 1 and 2: how the agent finds and keeps customers.');
  addChoice(form, 'Aapki book mein kitne customer hain?',
    ['Under 50', '50 to 100', '100 to 200', '200 to 400', 'More than 400']);
  addChoice(form, 'Pichhle mahine kitne naye customer jude?',
    ['None', '1 or 2', '3 to 5', '6 to 10', 'More than 10']);
  addChecks(form, 'Naye customer kaise milte hain?',
    ['Walks into shops and homes', 'Customers send people', 'The bank or society gives names', 'Family and neighbours', 'Does not look for new ones'],
    'Tick everything said.');
  addChoice(form, 'Ghar chalne layak book banane mein kitna time laga?',
    ['Under 6 months', '6 to 12 months', '1 to 3 years', 'Over 3 years', 'Still not enough', 'Got a ready book']);

  addSection(form, '3. The customers', 'Goal 3: who the customers are.');
  addChecks(form, 'Aapke customer kya kaam karte hain?',
    ['Shopkeepers', 'Street vendors', 'Homemakers', 'Daily-wage workers', 'Drivers', 'Salaried workers', 'Small workshop owners'],
    'Tick everything named.');
  addChoice(form, '10 customers mein se kitni auratein hain?',
    ['0 to 2', '3 to 5', '6 to 8', '9 or 10', "Doesn't know"]);
  addChoice(form, 'Zyada tar customer kis umar ke hain?',
    ['Mostly under 30', 'Mostly 30 to 50', 'Mostly over 50', 'All ages']);
  addChoice(form, 'Ek customer roz aam taur par kitna jama karta hai?',
    ['Under Rs 50', 'Rs 50 to 100', 'Rs 100 to 200', 'Rs 200 to 500', 'Over Rs 500', 'Varies a lot']);
  addChoice(form, '100 rupaye mein se kitne cash mein aate hain?',
    ['90 or more', '60 to 89', '40 to 59', '10 to 39', 'Under 10']);
  addChoice(form, '10 mein se kitne customers ke paas UPI hai?',
    ['0 to 2', '3 to 5', '6 to 8', '9 or 10', "Doesn't know"]);
  addChoice(form, '10 mein se kitne customers ka isi bank ya society se loan chal raha hai?',
    ['0 to 2', '3 to 5', '6 to 8', '9 or 10', "Doesn't know"]);
  addChoice(form, 'Pichhli baar kisi customer ka account poora hua, to usne paisa kis cheez mein lagaya?',
    ['Shop stock or business', 'Wedding or a function', 'School fees', 'Medical', 'Gold', 'Paid off a loan', 'Saved it again', "Doesn't know"]);

  addSection(form, '4. The tie to customers', 'Goal 1: do customers trust the agent, or the bank?');
  addChoice(form, 'Zyada tar customer kitne saal se aapke saath hain?',
    ['Under 1 year', '1 to 3 years', '3 to 5 years', 'Over 5 years', "Doesn't know"]);
  addChoice(form, 'Pichhli baar aap chhutti par the, to paisa kisne liya?',
    ['Someone the agent sent', 'Someone from the bank or society', 'Nobody; customers paid later', 'Customers went to the branch', 'Never took leave']);
  addChoice(form, 'Pichhle hafte kitne customers ne jama ke alawa kisi aur kaam mein madad maangi?',
    ['None', '1 to 5', '6 to 20', 'More than 20'],
    'Advice, a loan, a form, an emergency. Last week only.');
  addChoice(form, 'Pichhli baar aapne customers ko koi nayi cheez batayi, to 10 mein se kitno ne li?',
    ['Never suggested anything', '0 to 2', '3 to 5', '6 or more'],
    'A scheme, a loan, insurance. Count from that one time.');
  addChoice(form, 'Jab koi agent kaam chhod gaya, to uske customer kahan gaye?',
    ['Stayed with the bank or society', 'Went with the agent', 'Some each way', 'Stopped saving', 'Has not seen an agent leave']);

  addSection(form, '5. Pay and rules', 'Goal 1: what the agent earns, and what stops a second job. The most sensitive part.');
  addChoice(form, 'Collection par kitna percent milta hai?',
    ['No percent', 'Under 2%', '2 to 3%', '3 to 4%', '4% or more', "Doesn't know"],
    'Other for an exact rate.');
  addChoice(form, 'Fixed salary kitni hai?',
    ['No salary', 'Under Rs 8,000', 'Rs 8,000 to 15,000', 'Rs 15,000 to 25,000', 'Over Rs 25,000', 'Would not say']);
  addChoice(form, 'Pichhle mahine petrol ke baad ghar kitna le gaye?',
    ['Under Rs 8,000', 'Rs 8,000 to 15,000', 'Rs 15,000 to 25,000', 'Rs 25,000 to 40,000', 'Over Rs 40,000', 'Would not say'],
    'Do not react to the band.');
  addChoice(form, 'Jo customer khud branch ya phone se jama karne lage, un par aapko percent milta hai?',
    ['Yes, the same', 'Less', 'No', 'Has not happened', "Doesn't know"]);
  addChoice(form, 'Doosri jagah kaam karne par kya niyam hai?',
    ['No rule known', 'Told not to', 'Written in the contract', "Doesn't know"]);
  addChoice(form, 'Kya bank ya society ke paas aapka koi security deposit hai?',
    ['None', 'Under Rs 10,000', 'Rs 10,000 to 50,000', 'Over Rs 50,000', 'Would not say']);

  addSection(form, '6. Other offers, other agents', 'Goal 1: has anyone tried to hire agents, and how many agents are there?');
  addChoice(form, 'Pichhle ek saal mein kisi aur company ne aapse kaam ke liye baat ki?',
    ['No', 'Yes; said no', 'Yes; joined, still doing it', 'Yes; joined, then stopped']);
  addChoice(form, 'Woh company kis cheez ka kaam karti thi?',
    ['Savings or investment app', 'Loans', 'Insurance', 'A bank', 'Nobody asked'],
    'If a name comes up, type it in Other. Do not suggest one.');
  addChoice(form, 'Kyun?',
    ['Paid too little', 'Customers did not want it', 'The bank or society objected', 'Too much phone work', 'Did not trust it', 'Nobody asked'],
    'Ask only if a company asked. Tap the first reason given.');
  addChoice(form, 'Aap jaise kitne doosre agents ko naam se jaante ho?',
    ['None', '1 to 5', '6 to 20', 'More than 20', 'A number, no names']);
  addChoice(form, 'Unmein se kitne do jagah kaam karte hain?',
    ['None', '1 to 3', '4 to 10', 'More than 10', "Doesn't know"]);
  addChoice(form, 'Jinhone yeh kaam chhoda, woh ab kya karte hain?',
    ['Another collection job', 'Insurance or loan agent', 'A shop or business', 'A factory or office job', "Doesn't know", 'Knows no one who left']);

  addSection(form, '7. Thanks', 'Rs 300 now. Then one ask about more conversations. Not a job.');
  addChoice(form, 'Is baat ke 300 rupaye aapke hain.',
    ['Gave Rs 300', 'Refused']);
  addChoice(form, 'Aise aur logon se baat karwa sakte ho?',
    ['No', 'Will think', 'Yes, 1 or 2', 'Yes, 3 to 5', 'Yes, more than 5'],
    'No name or phone until offered.');

  addSection(form, '8. After the call. Do not ask.', 'Mark from the taps above. A hope is not a fact.');
  addText(form, 'Bank, society or app named without being asked', 'Leave blank if none.');
  addChoice(form, 'Could we hire this agent as street fleet?',
    ['Yes: no blockers', 'Maybe: one blocker', 'No: two or more blockers', 'Not clear'],
    'Blockers: no free time (8+ hour round, or another full job) · barred from a second job, or a deposit is stuck · ' +
    'phone for calls only · under 3 new customers last month · loses the percent when customers go digital · tried a company and left.');
  addChoice(form, 'The biggest blocker',
    ['None', 'No free time', 'Barred, or a deposit is stuck', 'Phone for calls only', 'Signs few new customers',
      'Loses pay when customers go digital', 'Tried a company and left', 'Not clear']);
  addChoice(form, 'How strong is the tie to the customers?',
    ['Strong: 4 or 5 signs', 'Medium: 2 or 3 signs', 'Weak: 0 or 1 sign', 'Not clear'],
    'Count the signs in section 4: most customers 3+ years · on leave, someone the agent sent collected, or customers paid later · ' +
    '6+ asked for other help last week · 3+ in 10 took the last suggestion · customers went with an agent who left.');
  addChoice(form, 'Decision',
    ['Talk to two more like this', 'Stop here', 'Not clear yet']);
  form.addParagraphTextItem().setTitle('One line: what surprised you?');

  const sheet = SpreadsheetApp.create('Janta deposit - could these agents be our fleet');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());
  Logger.log('Form: ' + form.getPublishedUrl());
  Logger.log('Edit: ' + form.getEditUrl());
  Logger.log('Sheet: ' + sheet.getUrl());
}

function addSection(form, title, help) {
  const page = form.addPageBreakItem().setTitle(title);
  if (help) page.setHelpText(help);
}
function addText(form, title, help) {
  const item = form.addTextItem().setTitle(title);
  if (help) item.setHelpText(help);
  return item;
}
function addChoice(form, title, options, help) {
  const item = form.addMultipleChoiceItem().setTitle(title).setChoiceValues(options).showOtherOption(true);
  if (help) item.setHelpText(help);
  return item;
}
function addChecks(form, title, options, help) {
  const item = form.addCheckboxItem().setTitle(title).setChoiceValues(options).showOtherOption(true);
  if (help) item.setHelpText(help);
  return item;
}
