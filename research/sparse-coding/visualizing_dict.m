function h=visualizing_dict(D,lambda2)

%show both, real and imaginary part
%sort per peak of maximum frequency 
d = D{lambda2};

[~, peak_lambda1s] = max(abs(d).^2, [], 1)

[~, sorting_indices] = sort(peak_lambda1s);


figure; 
subplot(121);
imagesc(real(d(:,sorting_indices)));title(['Real part for ' num2str(lambda2)])

subplot(122);
imagesc(imag(d(:,sorting_indices)));title(['Imaginary part for ' num2str(lambda2)]);