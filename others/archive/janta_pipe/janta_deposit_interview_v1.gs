/**
 * One phone call. You tap on his behalf. He is not being hired.
 *
 * Each item is one question. Read only that sentence. Do not read the choices.
 * Tap the nearest band. Other is for an exact number or a name.
 * No question offers him the two answers we are hoping for.
 *
 * Name, city, and area stay typed.
 * Rs 300 is thanks, at the end only. No customer name, no customer phone.
 * Do not say a company name, an app name, or any market-size number.
 *
 * How to run: script.google.com, blank project, paste, run createJantaDepositInterview.
 * Each run makes a new form. An older form will not update.
 */
function createJantaDepositInterview() {
  const form = FormApp.create('Janta deposit — why not these men?');
  form.setDescription(
    'Read one sentence. Tap one answer. Do not read the choices.\n' +
    'Other is for an exact number or a name.\n\n' +
    'Say this, then stop talking:\n' +
    '"Main aapka kaam samajhna chahta hoon. Roz ka paisa kaise jama hota hai, customer kaun hai, paisa kahan chala jata hai. ' +
    'Main naukri nahi de raha. Kisi customer ka naam ya phone nahi likhunga. Koi bhi sawaal chhod sakte ho."\n\n' +
    'Rs 300 only after the last spoken question, as thanks.'
  );
  form.setProgressBar(true);
  form.setAllowResponseEdits(true);
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false);
  form.setConfirmationMessage('Saved. Use the edit link if the call continues. No customer names.');

  const consent = form.addMultipleChoiceItem();
  consent.setTitle('Main apne liye likh raha hoon. Kisi customer ka naam ya phone nahi likhunga. Theek hai?');
  consent.setHelpText('Stop if he says no.');
  consent.setRequired(true);
  consent.setChoices([
    consent.createChoice('Yes', FormApp.PageNavigationType.CONTINUE),
    consent.createChoice('No. Stop.', FormApp.PageNavigationType.SUBMIT),
  ]);

  addDate(form, 'Date of the call');
  addText(form, 'Aapka naam kya hai?', 'His name.').setRequired(true);
  addText(form, 'Aap kis sheher mein kaam karte ho?', '').setRequired(true);
  addText(form, 'Aap kaun sa ilaaka cover karte ho?', 'Neighbourhood or route.');
  addText(form, 'Name he said on his own',
    'Bank, society, or app. Leave blank if he did not say one. Do not ask.');

  addSection(form, '1. His seat', 'One tap each. Do not explain the choices.');
  addChoice(form, 'Aap kitni jagah se jude ho?',
    '',
    ['One bank', 'One society', 'More than one', 'None']);
  addChoice(form, 'Roz ka route kaun tai karta hai?',
    '',
    ['The bank or society', 'He does', 'Both', 'He does not know']);
  addChoice(form, 'Aapko paisa kis hisaab se milta hai?',
    '',
    ['A salary', 'A percent of what he collects', 'Both', 'He keeps the profit', 'He does not know']);
  addChoice(form, 'Percent kitna hai?',
    'Other for a rate that is not in the list.',
    ['No percent', 'Under 2%', 'About 2.5%', 'About 3%', '4% or more', 'He does not know']);
  addChoice(form, 'Mahine ki salary kitni hai?',
    '',
    ['No salary', 'Under Rs 8,000', 'Rs 8,000 to 15,000', 'Rs 15,000 to 25,000', 'Over Rs 25,000', 'He does not know']);
  addChoice(form, 'Yeh paisa kaun deta hai?',
    '',
    ['The bank or society', 'The customer', 'Both', 'He does not know']);
  addChoice(form, 'Paisa kab milta hai?',
    '',
    ['The same day', 'Every week', 'Every month', 'When the account closes', 'He does not know']);
  addChoice(form, 'Pichhle mahine ghar kitna le gaye?',
    'After petrol. Do not react to the band.',
    ['Under Rs 8,000', 'Rs 8,000 to 15,000', 'Rs 15,000 to 25,000', 'Rs 25,000 to 40,000', 'Over Rs 40,000', 'He would not say']);
  addChoice(form, 'Security deposit pada hai?',
    '',
    ['None', 'Under Rs 10,000', 'Rs 10,000 to 50,000', 'Over Rs 50,000', 'He would not say']);
  addChoice(form, 'Collections kam hon to kya hota hai?',
    '',
    ['Nothing', 'A warning', 'They keep the deposit', 'They take the route', 'He does not know']);
  addChoice(form, 'Doosri jagah kaam karne par kya niyam hai?',
    '',
    ['No rule he knows of', 'They have told him not to', 'It is written', 'He does not know']);
  addChoice(form, 'Aap jaise kitne logon ko aap naam se jaante ho?',
    '',
    ['None', '1 to 5', '6 to 20', 'More than 20', 'He gave a number but no names']);

  addSection(form, '2. His day', 'Tap what he just said.');
  addChoice(form, 'Roz kitne ghante chalte ho?',
    '',
    ['Under 4 hours', '4 to 6 hours', '6 to 8 hours', 'More than 8 hours']);
  addChoice(form, 'Ek din mein kitni jagah ruktay ho?',
    '',
    ['Under 30', '30 to 60', '60 to 100', 'More than 100']);
  addChoice(form, 'Shaam ko paisa kahan jata hai?',
    '',
    ['The branch or society, same day', 'An app records it', 'He holds it overnight', 'His own account', 'He does not handle the cash']);
  addChoice(form, 'Koi paise na de to aap kya karte ho?',
    '',
    ['Comes back the next day', 'Marks a miss and moves on', 'Someone else pays', 'The institution follows up', 'That day is lost']);
  addChoice(form, 'Kal kitne logon se paisa liya?',
    '',
    ['Under 20', '20 to 50', '50 to 100', 'More than 100', 'Yesterday was not a normal day']);
  addChoice(form, 'Kal kul kitne rupaye aaye?',
    '',
    ['Under Rs 5,000', 'Rs 5,000 to 20,000', 'Rs 20,000 to 50,000', 'Over Rs 50,000', 'He does not know']);
  addChoice(form, 'Paisa kis tarah aata hai?',
    '',
    ['Cash', 'Phone or UPI', 'Both', 'Not daily']);
  addChoice(form, '100 rupaye mein se kitne cash hain?',
    '',
    ['Not applicable', '90 or more', '60 to 90', 'About half', 'Under 40', 'Almost none']);
  addChecks(form, 'Customer ko kya milta hai?',
    'Tick only words he used.',
    ['Interest', 'A passbook', 'A loan', 'Insurance', 'A receipt', 'He did not say']);
  addChecks(form, 'Customer kaun hain?',
    'Tick only words he used.',
    ['Shopkeepers', 'Households', 'Salaried people', 'Drivers or delivery', 'Small factory owners', 'Farmers']);
  addChoice(form, 'Book par kitne log hain?',
    '',
    ['Under 50', '50 to 100', '100 to 200', '200 to 400', 'More than 400']);
  addChoice(form, 'Ek aadmi roz kitna deta hai?',
    '',
    ['Under Rs 20', 'Rs 20 to 50', 'Rs 50 to 100', 'Rs 100 to 200', 'More than Rs 200', 'It varies']);
  addChoice(form, '10 mein se kitne logon par loan chal raha hai?',
    '',
    ['0 to 2', '3 to 5', '6 to 8', '9 or 10', 'He does not know']);

  addSection(form, '3. Loans and apps', 'One tap each.');
  addChoice(form, 'Kya aap loan karwate ho?',
    '',
    ['Yes', 'Sometimes', 'No', 'Someone else at the branch does']);
  addChoice(form, 'Loan kitne ka hota hai?',
    '',
    ['He does not arrange one', 'Under Rs 25,000', 'Rs 25,000 to 1 lakh', 'Rs 1 to 3 lakh', 'Rs 3 to 5 lakh', 'Above Rs 5 lakh']);
  addChoice(form, 'Loan par aapko kya milta hai?',
    '',
    ['Nothing', 'A one-time amount', 'A percent', 'He does not know']);
  addChoice(form, '10 mein se kitno ki ITR hoti hai?',
    '',
    ['0 to 2', '3 to 5', '6 to 8', '9 or 10', 'He does not know']);
  addChoice(form, 'Bina ITR loan hota hai?',
    '',
    ['Yes', 'Sometimes', 'No', 'He does not know']);
  addChecks(form, 'Bina ITR kaun sa kagaz chalta hai?',
    'Tick only papers he named.',
    ['Aadhaar', 'A shop bill or photo', 'The passbook', 'A guarantor', 'No other paper', 'He does not know']);
  addChoice(form, 'Customer jama kyun karte hain?',
    '',
    ['For a loan', 'For the interest', 'For a goal, such as a wedding', 'It is a habit', 'He has not asked']);
  addChoice(form, 'Kya aap kisi app se jude ho?',
    'If he names one, type it in Other. Do not suggest a name.',
    ['No', 'The bank or society app', 'A savings app', 'Both', 'An app asked. He said no.']);
  addChoice(form, 'Us app mein aap kya karte ho?',
    '',
    ['No app', 'Enter the collection', 'A reminder', 'Bring people to a savings app', 'He refused it']);
  addChoice(form, 'Us app se mahine kitna milta hai?',
    '',
    ['No app', 'Nothing', 'Under Rs 2,000', 'Rs 2,000 to 8,000', 'Over Rs 8,000', 'He did not say']);

  addSection(form, '4. What he has seen', 'Ask about a thing that already happened. Skip any guess about the future.');
  addChoice(form, 'Naya aadmi kitne mahine mein ghar ka kharcha nikalne layak book bana leta hai?',
    '',
    ['Under 1 month', '1 to 3 months', '3 to 6 months', '6 to 12 months', 'More than a year', 'He has not seen a new man']);
  addChoice(form, 'Aapki book itni hone mein kitna time laga?',
    '',
    ['Under 6 months', '6 to 12 months', '1 to 3 years', 'More than 3 years', 'He was given a ready book']);
  addChoice(form, 'Naye aadmi ko customer kitne time baad roz ka paisa dene lagta hai?',
    '',
    ['The same day', 'A few days', '1 to 4 weeks', '1 to 3 months', 'Longer than 3 months', 'He has not seen it']);
  addChoice(form, 'Kisi agent ke jaane ke baad customer kahan ruka?',
    '',
    ['With the bank or society', 'With the agent', 'Some with each', 'He has not seen an agent leave']);
  addChoice(form, 'Us story ka sabse bada kaaran kya tha?',
    '',
    ['A loan', 'Money already saved', 'The institution', 'The agent', 'The family', 'He did not say', 'No such story']);
  addChoice(form, 'Aap beemar hon to agle din chakkar kaun karta hai?',
    '',
    ['His own person', 'The institution sends someone', 'The round waits', 'This has not happened']);
  addChoice(form, 'Kya aapne do jagah kaam karta hua koi agent dekha hai?',
    '',
    ['Yes', 'No', 'He is not sure']);
  addChoice(form, 'Jab institution ko pata chala to kya hua?',
    '',
    ['They allowed it', 'He hid it', 'He was removed', 'Nothing', 'He has not seen this']);
  addChoice(form, 'Kisi customer ne kaha hai ki aap roz mat aana?',
    '',
    ['Yes', 'No', 'He does not remember']);
  addChoice(form, 'Us customer par aapki kamai ka kya hua?',
    '',
    ['It stopped', 'It fell', 'No change', 'This has not happened']);
  addChoice(form, 'Account beech mein band ho to jama paisa kya hota hai?',
    '',
    ['It stays there', 'The customer can take it', 'He does not know']);
  addChoice(form, 'Jaldi band karne par koi katauti hoti hai?',
    '',
    ['No', 'The interest is cut', 'There is a charge', 'Interest is cut and there is a charge', 'He does not know']);
  addChoice(form, 'Deposit band ho aur loan chal raha ho, to loan ka kya hota hai?',
    '',
    ['The loan stays there', 'The loan can move', 'There is no loan', 'He does not know']);
  addChoice(form, '10 mein se kitno ke paas UPI hai?',
    '',
    ['0 to 2', '3 to 5', '6 to 8', '9 or 10', 'He does not know']);
  addChoice(form, 'Kya koi customer aapko phone se paisa bhejta hai?',
    '',
    ['Often', 'Sometimes', 'Almost never', 'Never']);
  addChoice(form, 'Naam se jaane hue agents mein se kitne do jagah kaam karte hain?',
    '',
    ['None', '1 to 3', '4 to 10', 'More than 10', 'He does not know']);

  addSection(form, '5. Thanks', 'Rs 300 now. Then one ask about more conversations. Not a job.');
  addChoice(form, 'Is baat ke 300 rupaye aapke hain.',
    '',
    ['Gave him Rs 300', 'He refused']);
  addChoice(form, 'Aise aur logon se baat karwa sakte ho?',
    '',
    ['Yes', 'He will think', 'No']);
  addChoice(form, 'Kitne logon se?',
    '',
    ['None', '1 or 2', '3 to 5', 'More than 5']);
  addChecks(form, 'Kaise milwaoge?',
    'No name and no phone until he offers them.',
    ['On a phone call', 'He will bring them', 'He will ask someone else', 'He did not say']);

  addSection(form, '6. After the call. Do not ask.',
    'Mark from the taps above. A hope he stated is not a fact.');
  addChoice(form, 'Is his job the wealth-app job?',
    'Cash into a bank or society, for interest and a loan, is a different job from a daily phone payment into a fund.',
    ['Different job', 'He uses an app, and the money still lands in the bank or society', 'Customers already pay him by phone', 'Not clear']);
  addChoice(form, 'Does the book come with the man?',
    '',
    ['In a story he saw, customers followed the agent',
      'In a story he saw, customers stayed',
      'He has not seen an agent leave',
      'Not clear']);
  addChoice(form, 'Can a commission pay men like him?',
    'A liquid-fund trail is about 0.05 to 0.15 percent of the balance a year. His pay is a percent of cash collected. Matching it means a bounty or a salary.',
    ['His take-home is small enough that a small bounty could clear it',
      'He lives on a percent of collections',
      'He is staff, or a deposit is stuck',
      'He would not give the number']);
  addChoice(form, 'Is the crowd real, and free to move?',
    '',
    ['He named many, and some already work two places',
      'He named many, and the institution bars a second place',
      'He knows only a few by name',
      'He is unusual']);
  addChoice(form, 'Decision on this specimen',
    '',
    ['Worth talking to two more men',
      'The man can be found. The customers stay, so the book starts empty',
      'Only if a loan and the saved balance are also replaced',
      'His pay depends on the rupee staying where it is',
      'Not clear yet']);
  addChoice(form, 'The one fact that decided it',
    'Use Other for the number or the story.',
    ['His percent of the cash',
      'Where customers stayed when an agent left',
      'A deposit, or a bar on other work',
      'The loan',
      'Customers do not pay by phone',
      'He could not name other men',
      'Not clear']);

  const sheet = SpreadsheetApp.create('Janta deposit - why not these men');
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
function addDate(form, title) {
  form.addDateItem().setTitle(title);
}
function addChoice(form, title, help, options) {
  const item = form.addMultipleChoiceItem().setTitle(title).setChoiceValues(options).showOtherOption(true);
  if (help) item.setHelpText(help);
  return item;
}
function addChecks(form, title, help, options) {
  const item = form.addCheckboxItem().setTitle(title).setChoiceValues(options).showOtherOption(true);
  if (help) item.setHelpText(help);
  return item;
}
